# DBTermPrj

예약제 시간 당 한 팀만을 받아 운영하는 ‘원테이블 식당’을 위한 DB 기반 프로그램을 통해 판매할 메뉴, 예약 현황, 수입
현황을 관리하고자 한다. 이에 따라 필요한 데이터베이스를 설계하고, 프로그램을 구현하였다. 데이터베이스는 mySQL 을
사용하고 프로그램 구현을 위한 웹 프레임워크로 flask 를 사용하였다.


![image](https://github.com/user-attachments/assets/d3eb4cad-0370-43b9-abbb-c832cf2ae1fd)




![image](https://github.com/user-attachments/assets/7902044e-6cbd-4148-b5f1-ad69d5f8ccaa)
![image](https://github.com/user-attachments/assets/6f7e7368-9d64-4dce-b417-97b519bfe596)
![image](https://github.com/user-attachments/assets/b79f7912-a25b-494e-8173-f11ad8dbb5ee)



# 트리거적용
1. 메뉴의 판매상태가 N 으로 바뀌면, 시스템 날짜 이후의 예약건에 대해서 해당 메뉴주문 건을 삭제한다. 삭제 후 해당
예약건의 주문 메뉴가 아무것도 존재하지 않으면, 해당 예약건을 삭제한다.
2. 메뉴의 판매상태가 N 으로 바뀌면, 시스템 날짜 이후의 예약건에 대해서 totalPrice 를 업데이트한다.
3. 메뉴의 가격을 변경시, 시스템 날짜 이후의 예약건에 대해서만 가격이 변경된다. 

_메뉴 속성 변경에 대한 예약건 업데이트
방문 당일의 메뉴 상태에 대해 결제. 
시스템 날짜(CURRENT_DATE) 고려_


