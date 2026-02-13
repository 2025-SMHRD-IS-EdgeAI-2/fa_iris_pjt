## AI 기반 개인 맞춤형 학습 페이스 메이커
# 팀명 : FA-IRIS 
<img width="1027" height="484" alt="image" src="https://github.com/user-attachments/assets/32ec5ed4-29bc-4ae5-bbbd-df70aa85cc5c" />

## 서비스 소개
* 서비스명 : 집중도와 스트레스 지수 측정을 통한 학습 페이스 메이커 구현
* 서비스 설명
  - 웹캠을 통하여 안면과 눈 중심 측정, 집중도를 수치화 후 사용자에게 하루 평균 집중 점수를 제공
  - 제작된 디바이스 센서를 통하여 심박 변이도, 산소 포화도, 피부 전도도를 측정하여 스트레스 지수를 산출 및 사용자에게 제공
  - 측정된 집중도와 스트레스 지수를 통하여 생성형 AI를 통한 피드백 출력 및 사용자에 제공
  - 다이어리 기능을 통해 피드백 내용과 점수를 보고 하루 학습에 대한 회고 진행
<img width="881" height="675" alt="image" src="https://github.com/user-attachments/assets/5c464de1-cb24-46b9-b19a-d5ad3d9d9d3e" />

## 프로젝트 기간
* 2026.01.29 ~ 2026.02.13

## 주요기능
* 영상 분석 기술 - 눈의 크기, 눈 깜박임 횟수, 얼굴의 움직임, 표정 변화
* 센서류를 활용한 신체 활동 측정 - 심박 변이도, 피부 전도도, 산소포화도
* 측정된 점수를 통한 LLM 서비스를 활용하여 피드백 도출
* 학습 일지, 자가 평가 등의 기록 저장 및 날짜별 확인 기능

## 기술스택
<table>
    <tr>
        <th>구분</th>
        <th>내용</th>
    </tr>
    <tr>
        <td>사용언어</td>
        <td>
            <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"/> 
            <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=HTML5&logoColor=white"/>
            <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=CSS3&logoColor=white"/>
            <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=white"/>
        </td>
    </tr>
    <tr>
        <td>라이브러리</td>
        <td>
            <img src="https://img.shields.io/badge/Mediapip-0097A7?style=for-the-badge&logo=mediapipe&logoColor=white"/>
        </td>
    </tr>
    <tr>
        <td>개발도구</td>
        <td>
            <img src="https://img.shields.io/badge/RaskpberryPi-A22846?style=for-the-badge&logo=RaskpberryPi&logoColor=white"/>
            <img src="https://img.shields.io/badge/VSCode-007ACC?style=for-the-badge&logo=VisualStudioCode&logoColor=white"/>
        </td>
    </tr>
    <tr>
        <td>서버환경</td>
        <td>
            <img src="https://img.shields.io/badge/node.js-5FA04E?style=for-the-badge&logo=node.js&logoColor=white"/>
            <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"/>
        </td>
    </tr>
    <tr>
        <td>데이터베이스</td>
        <td>
            <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white"/>
        </td>
    </tr>
    <tr>
        <td>협업도구</td>
        <td>
            <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white"/>
            <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white"/>
        </td>
    </tr>
</table>

* 주요 활용 언어 : python(Back-end), JavaScript(Front-end)
* Front-End 세부 스택 : HTML, CSS, node.js
* Back-End / HW 세부 스택 : Mediapipe lib(대표 라이브러리), Thonny(라즈베리파이 구동)
* 통합 개발 환경 : VS code
* DataBase : MySQL
* 형상 관리 도구 : GitHub

## 시스템 아키텍처
<img width="971" height="561" alt="image" src="https://github.com/user-attachments/assets/d5bdcd17-20e3-4cfd-9c29-2a8fab8a1862" />

## 유스 케이스
<img width="920" height="574" alt="image" src="https://github.com/user-attachments/assets/5e04b9b6-56fd-46bc-af92-480e2120274b" />

## 서비스 흐름도


## ER 다이어그램
<img width="960" height="556" alt="image" src="https://github.com/user-attachments/assets/8e6dd0d8-11dc-48d3-a5c7-6c0e827fc873" />

## 화면구성
* ON-BOARDING / 시작 / 로그인
<img width="1071" height="439" alt="image" src="https://github.com/user-attachments/assets/24eea75a-28c4-4d0b-8be2-1b288fff4ede" />
  
* 측정치 출력 화면(당일, 일자별)
<img width="624" height="451" alt="image" src="https://github.com/user-attachments/assets/143ff299-a6fd-4706-8c4b-c845e55151fa" />
  
* 다이어리 기입 및 자격증 관리 화면



## 팀원 역할

## 트러블 슈팅
