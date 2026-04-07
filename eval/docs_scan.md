## module-index.md

- 기능: 백엔드 전체 모듈 인덱스다. auth, user, weather, region,
  outfit, notification, notice, file-storage, platform-init 문서를 연결
  한다.
- 핵심 파일: doc/module-auth-authorization.md, doc/module-user.md,
  doc/module-weather.md, doc/module-region.md, doc/module-outfit.md
- 질문 후보: 인증 관련 문서는 어디부터 보면 돼? / 날씨-코디 연계 구조
  를 보려면 어떤 문서들을 읽어야 해?

## module-auth-authorization.md

- 기능: 로그인, OAuth, JWT 인가, 토큰 재발급, 이메일 인증을 담당한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  AuthController.java, backend/java/com/boram/look/global/config/
  SecurityConfig.java, backend/java/com/boram/look/global/security/
  JwtProvider.java, backend/java/com/boram/look/global/security/oauth/
  CustomOAuth2LoginSuccessHandler.java, backend/java/com/boram/look/
  global/security/reissue/TokenReissueFilter.java, backend/java/com/
  boram/look/service/auth/EmailVerificationService.java
- 질문 후보: OAuth 로그인 시작 URL은 어디서 처리돼? / OAuth 성공 후
  내부 JWT 생성은 어느 파일이 담당해? / 리프레시 토큰 재발급 검증은 어
  디에 있어? / 인증 없이 허용되는 URL 목록은 어디서 정의돼? / 이메일 인
  증 코드는 어느 서비스가 처리해?

## module-weather.md

- 기능: 단기예보, 중기예보, 미세먼지, 자외선 데이터를 수집·저장·캐시
  하고 조회 API로 제공한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  WeatherController.java, backend/java/com/boram/look/service/weather/
  WeatherFacade.java, backend/java/com/boram/look/service/weather/
  forecast/ForecastScheduler.java, backend/java/com/boram/look/service/
  weather/mid/MidTermForecastScheduler.java, backend/java/com/boram/
  look/service/weather/air/AirQualityScheduler.java, backend/java/com/
  boram/look/service/weather/uv/UvIndexScheduler.java
- 질문 후보: 현재~24시간 날씨 조회 API는 어디서 처리돼? / 날씨 데이터
  를 한 DTO로 조합하는 곳은 어디야? / 단기예보 배치 수집은 어느 스케줄
  러가 담당해? / 중기예보 재수집 로직은 어디를 봐야 해? / 자외선 데이터
  수집 스케줄러는 어디에 있어?

## module-outfit.md

- 기능: 날씨·상황·성별 기반 코디 추천과 코디 메타데이터 관리를 담당한
  다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  OutfitController.java, backend/java/com/boram/look/api/controller/
  OutfitConditionController.java, backend/java/com/boram/look/service/
  outfit/OutfitFacade.java, backend/java/com/boram/look/service/outfit/
  OutfitService.java, backend/java/com/boram/look/service/outfit/
  OutfitConditionService.java
- 질문 후보: 코디 추천 요청은 어느 컨트롤러에서 받아? / 날씨와 이벤트
  조건을 합쳐 코디를 고르는 곳은 어디야? / 코디 온도 범위 목록은 어느
  API에서 조회해? / 로그인 사용자의 북마크 상태를 포함해 응답하는 곳은
  어디야?

## module-user.md

- 기능: 회원가입, 프로필 수정, 비밀번호 변경, 탈퇴, 북마크, 탈퇴 사유
  조회를 담당한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  UserController.java, backend/java/com/boram/look/api/controller/
  BookmarkController.java, backend/java/com/boram/look/api/controller/
  DeleteReasonController.java, backend/java/com/boram/look/service/
  user/UserService.java, backend/java/com/boram/look/service/user/
  BookmarkService.java, backend/java/com/boram/look/service/user/
  DeleteReasonService.java
- 질문 후보: 회원가입은 어느 API와 서비스가 처리해? / 비밀번호 변경
  로직은 어디를 봐야 해? / 회원 탈퇴 시 삭제 이력을 저장하는 곳은 어디
  야? / 북마크 추가·삭제는 어느 서비스가 담당해?

## module-notification.md

- 기능: FCM 토큰 관리, 알림 설정 저장, 정기 푸시 발송을 담당한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  NotificationController.java, backend/java/com/boram/look/service/
  notification/FcmTokenService.java, backend/java/com/boram/look/
  service/notification/UserNotificationSettingService.java, backend/
  java/com/boram/look/service/notification/
  NotificationSchedulerService.java, backend/java/com/boram/look/
  service/notification/SendNotificationJob.java
- 질문 후보: 디바이스 FCM 토큰은 어디에 저장돼? / 알림 설정을 바꾸면
  Quartz Job을 다시 등록하는 곳은 어디야? / 실제 푸시 발송 작업은 어떤
  Job이 수행해? / 사용자의 알림 설정 조회 API는 어디에 있어?

## module-notice.md

- 기능: 공지사항 게시글과 공지 이미지를 생성, 수정, 조회, 삭제한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  NoticeController.java, backend/java/com/boram/look/service/notice/
  NoticeService.java, backend/java/com/boram/look/domain/notice/
  Notice.java, backend/java/com/boram/look/domain/notice/
  NoticeImage.java
- 질문 후보: 공지사항 생성 API는 어디야? / 공지 이미지 업로드 후 본문
  과 연결하는 흐름은 어디서 처리해? / 공지 목록 조회 로직은 어느 서비스
  에 있어?

## module-region.md

- 기능: GeoJSON/DB 기반 행정구역을 로딩해 좌표를 지역 코드로 변환한
  다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  RegionController.java, backend/java/com/boram/look/service/region/
  RegionService.java, backend/java/com/boram/look/service/region/
  RegionCacheService.java, backend/java/com/boram/look/service/region/
  GeoJsonRegionMapper.java
- 질문 후보: 좌표로 지역을 찾는 API는 어디에 있어? / 서버 시작 시 지
  역 캐시를 적재하는 곳은 어디야? / Point-in-Polygon 방식 지역 탐색은
  어느 모듈을 봐야 해? / GeoJSON 업로드 처리는 어디서 해?

## module-file-storage.md

- 기능: 관리자 파일 업로드/삭제와 Presigned URL 발급을 담당한다.
- 핵심 파일: backend/java/com/boram/look/api/controller/
  S3Controller.java, backend/java/com/boram/look/service/s3/
  S3FileService.java, backend/java/com/boram/look/service/s3/
  FileMetadataService.java, backend/java/com/boram/look/service/s3/
  FileFacade.java
- 질문 후보: 관리자 파일 업로드는 어느 API에서 처리돼? / S3 파일 삭제
  로직은 어디야? / Presigned URL 발급은 어느 서비스가 맡아? / 파일 바이
  너리 저장과 메타데이터 저장 책임은 어떻게 나뉘어?

## module-platform-init.md

- 기능: 서버 기동 시 필수 캐시와 데이터를 초기화하고 운영용 헬스 체크
  를 제공한다.
- 핵심 파일: backend/java/com/boram/look/service/InitService.java,
  backend/java/com/boram/look/service/InitAsyncService.java, backend/
  java/com/boram/look/api/controller/HealthController.java
- 질문 후보: 서버 시작 시 초기화 진입점은 어디야? / 비동기 날씨 캐시
  선적재는 어느 서비스가 담당해? / 헬스 체크 API와 캐시 재초기화 API는
  어디에 있어?