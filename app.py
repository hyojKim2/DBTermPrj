from flask import (Flask, request, 
render_template, redirect, url_for, flash,  jsonify
)
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 플래시 메시지를 위한 키 설정

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'db': 'termprj',
    'charset': 'utf8'
}




@app.route('/')
def home():
    return render_template('index.html')

# 관리자 로그인 페이지
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # 입력된 ID와 PW 가져오기
        input_id = request.form['id']
        input_pw = request.form['pw']

        # 데이터베이스 연결 및 조회
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = "SELECT id, pw FROM admin WHERE id = %s"
            cursor.execute(query, (input_id,))
            result = cursor.fetchone()  # 쿼리 결과 가져오기

            if result and result[1] == input_pw:  # ID가 존재하고, PW가 일치하면
                flash("로그인 성공!", "success")
                return redirect(url_for('admin_dashboard'))  # 대시보드 페이지로 리다이렉트
            else:
                flash("아이디 또는 비밀번호가 잘못되었습니다.", "danger")
        except Exception as e:
            flash(f"데이터베이스 연결 실패: {e}", "danger")
        finally:
            conn.close()

    # 로그인 HTML 템플릿 렌더링
    return render_template('admin_login.html')



# 관리자 대시보드
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# 수입 확인 페이지
@app.route('/admin-income', methods=['GET', 'POST'])
def admin_income():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # GET 요청 (수입 데이터 조회)
    if request.method == 'GET':
        # income 테이블에서 모든 데이터를 가져옵니다
        cursor.execute("SELECT * FROM income ORDER BY date desc")
        income_data = cursor.fetchall()

    # POST 요청 (수입 갱신)
    if request.method == 'POST':
        # 오늘 이전의 예약 정보를 가져와 income 테이블에 삽입 또는 갱신
        cursor.execute("""INSERT INTO income (date, earn)
            SELECT b.date, SUM(b.totalPrice) as earn
            FROM booklist b
            WHERE b.date < CURRENT_DATE
            GROUP BY b.date
            ON DUPLICATE KEY UPDATE earn = VALUES(earn);

        """)
        conn.commit()

        # 수입 갱신 후 income 테이블에서 데이터를 가져옵니다
        cursor.execute("SELECT * FROM income ORDER BY date DESC")
        income_data = cursor.fetchall()

    # 연결 종료
    conn.close()

    return render_template('admin_income.html', income_data=income_data)


#예약 삭제 처리 
@app.route('/delete-booking', methods=['POST'])
def delete_booking():
    try:
        # 클라이언트에서 받은 예약 날짜와 시간
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')

        # 데이터베이스에서 해당 예약 삭제
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # bookdetail과 bookList 삭제
        delete_bookdetail_query = """
        DELETE FROM bookdetail WHERE date = %s AND time = %s
        """
        delete_booklist_query = """
        DELETE FROM booklist WHERE date = %s AND time = %s
        """

        cursor.execute(delete_bookdetail_query, (date, time))
        cursor.execute(delete_booklist_query, (date, time))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Booking deleted successfully'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to delete booking'}), 500




# 예약 현황 페이지
@app.route('/admin-booking')
def admin_booking():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # bookList 테이블에서 모든 예약 정보 가져오기
        cursor.execute("SELECT * FROM bookList")
        booking_list = cursor.fetchall()

    except Exception as e:
        print(f"DB 오류: {e}")
        booking_list = []
    finally:
        conn.close()

    return render_template('admin_booking.html', booking_list=booking_list)

@app.route('/admin-menu', methods=['GET', 'POST'])
def admin_menu():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if request.method == 'POST':
            if 'add_menu' in request.form:
                # 새 메뉴 추가
                menu_name = request.form['menu_name']
                menu_price = request.form['menu_price']
                cursor.execute("""
                    INSERT INTO menu (name, price)
                    VALUES (%s, %s)
                """, (menu_name, menu_price))
                conn.commit()

            elif 'update_menu' in request.form:
                # 가격만 수정 (이름은 그대로)
                menu_name = request.form['menu_name']
                new_menu_price = request.form['new_menu_price']
                cursor.execute("""
                    UPDATE menu
                    SET price = %s
                    WHERE name = %s
                """, (new_menu_price, menu_name))
                conn.commit()

            elif 'delete_menu' in request.form:
                # 메뉴 판매 상태 변경
                menu_name = request.form['menu_name']
                cursor.execute("""
                    UPDATE menu
                    SET orderState = CASE 
                                        WHEN orderState = 'N' THEN 'Y'
                                        WHEN orderState = 'Y' THEN 'N'
                                    END
                    WHERE name = %s;
                """, (menu_name,))
                conn.commit()

        # 메뉴 리스트 가져오기
        cursor.execute("""
                       SELECT name, price, orderState 
                       FROM menu order by OrderState desc, name
                       """)
        menu_list = cursor.fetchall()

    except Exception as e:
        print(f"DB 오류: {e}")
        menu_list = []
    finally:
        conn.close()

    return render_template('admin_menu.html', menu_list=menu_list)


@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        # 예약 정보 처리
        date = request.form['date']
        time = request.form['time'][:2]  # 시간에서 앞 두자리만 사용 (11:00 -> 11)
        menu_items = request.form.getlist('menu')  # 선택한 메뉴들
        menu_counts = request.form.getlist('menu_count')  # 각 메뉴의 수량
        name = request.form['name']
        phone = request.form['phone']
        people_count = request.form['people_count']

        # 선택한 메뉴들의 가격 합산
        total_price = 0
        for i, menu in enumerate(menu_items):
            menu_name, menu_price = menu.split('-')
            menu_price = int(menu_price)
            menu_count = int(menu_counts[i])
            total_price += menu_price * menu_count

        # 데이터베이스 연결 및 예약 정보 저장
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # 예약 정보 저장
            query_booklist = """
                INSERT INTO bookList (date, time, personName, phoneNumber, headCount, totalPrice)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_booklist, (date, time, name, phone, people_count, total_price))
            conn.commit()

            # 예약된 id 가져오기
            booking_id = cursor.lastrowid
            print(f"Booking ID: {booking_id}")

            # 메뉴 정보 저장
            menu_num = 1  # 메뉴 번호 초기화
            for i, menu in enumerate(menu_items):
                menu_name, menu_price = menu.split('-')
                menu_count = menu_counts[i]
                
                query_detail = """
                    INSERT INTO bookdetail (menunum, date, time, menuName, menuCnt)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query_detail, (menu_num, date, time, menu_name, menu_count))
                menu_num += 1  # 다음 메뉴에 대해 menunum을 1씩 증가시킴
            conn.commit()

            flash("예약이 완료되었습니다!", "success")
            return redirect(url_for('home'))  # 예약이 완료되면 메인 화면으로 리다이렉트

        except Exception as e:
            flash(f"예약 실패: {e}", "danger")
            print(f"Error: {e}")  # 예외 메시지 출력

        finally:
            conn.close()

    # 메뉴 데이터 불러오기
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM menu where orderState='Y' order by name")
        menu_items = cursor.fetchall()
    except Exception as e:
        flash(f"메뉴 로드 실패: {e}", "danger")
        print(f"Error loading menu: {e}")  # 예외 메시지 출력
        menu_items = []
    finally:
        conn.close()

    return render_template('reserve.html', menu_items=menu_items)

#예약디테일
@app.route('/get-details', methods=['POST'])
def get_details():
    date = request.json.get('date')
    time = request.json.get('time')

    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # bookdetail 테이블에서 해당 예약의 세부 정보 가져오기
        query = """
            SELECT menuName, menuCnt
            FROM bookdetail
            WHERE date = %s AND time = %s
        """
        cursor.execute(query, (date, time))
        details = cursor.fetchall()

    except Exception as e:
        print(f"DB 오류: {e}")
        return {'error': str(e)}, 500
    finally:
        conn.close()

    return {'details': details}, 200



if __name__ == '__main__':
    app.run(debug=True)
