# 대한민국 아트 시계

TV 브라우저에서 GitHub Pages 주소로 접속해서 큰 시계처럼 쓰는 정적 웹페이지입니다.

## 들어있는 기능

- 대한민국 기준 시간 표시
- 큰 시계 UI
- 날짜 표시
- 서울 기본, 선택 도시 기준 온도, 습도, 체감온도, 날씨 표시
- 화면에서 주요 한국 도시 선택
- 선택 도시 기준 오늘의 날씨 요약과 생활 팁 표시
- 한국시간 기준 자동 야간 모드
- Cleveland Museum of Art CC0 명화/자연/정물 이미지 100장 로컬 asset 배경 자동 전환
- 다음 배경 이미지 사전 로드로 TV 브라우저에서도 부드러운 전환
- 로컬 명화 asset 로딩 실패 시 기본 배경으로 자동 대체
- 공개 도메인 선율 기반 클래식 루프 및 절차적 자연 소리 선택 재생
- 연속재생/한곡반복/무작위 음악 모드, 볼륨 조절, 출처/라이선스 표시
- 생활형 카운트다운 타이머와 KST 단일 알람
- 타이머/알람 종료 시 화면 알림, Web Audio 차임, 음악 볼륨 자동 낮춤
- TV/OLED 번인 위험을 줄이기 위한 아주 약한 위치 이동
- 전체화면 버튼

## 바로 실행하기

압축을 풀고 `index.html`을 브라우저로 열면 됩니다.

GitHub Pages에 올릴 때는 이 폴더 안의 파일을 그대로 저장소 루트에 업로드하면 됩니다. 배포 후 주소는 아래와 같습니다.

```text
https://sungreong.github.io/korea-art-clock/
```

## GitHub Pages 배포 방법

1. GitHub 저장소 `sungreong/korea-art-clock`에 이 폴더의 파일을 저장소 루트로 푸시합니다.
2. 저장소의 `Settings`로 이동합니다.
3. `Pages` 메뉴를 엽니다.
4. `Deploy from a branch`를 선택합니다.
5. Branch는 `main`, folder는 `/root`로 선택합니다.
6. 배포 후 `https://sungreong.github.io/korea-art-clock/` 주소로 TV에서 접속합니다.

## 지역 바꾸기

기본 날씨는 서울입니다. 화면 오른쪽 위 `도시선택` 버튼에서 주요 도시를 고를 수 있습니다.

URL 뒤에 좌표를 붙여 직접 지정할 수도 있습니다. URL 옵션은 저장된 도시보다 우선합니다.

예시:

```text
?city=부산&lat=35.1796&lon=129.0756
```

전체 예시:

```text
https://아이디.github.io/저장소명/?city=부산&lat=35.1796&lon=129.0756
```

자주 쓰는 좌표:

```text
서울: ?city=서울&lat=37.5665&lon=126.9780
부산: ?city=부산&lat=35.1796&lon=129.0756
대구: ?city=대구&lat=35.8714&lon=128.6014
인천: ?city=인천&lat=37.4563&lon=126.7052
광주: ?city=광주&lat=35.1595&lon=126.8526
대전: ?city=대전&lat=36.3504&lon=127.3845
제주: ?city=제주&lat=33.4996&lon=126.5312
```

## 옵션

초 숨기기:

```text
?seconds=off
```

날씨 끄기:

```text
?weather=off
```

오늘 날씨 요약 패널만 끄기:

```text
?summary=off
```

야간 모드 강제 켜기:

```text
?night=on
```

야간 모드 끄기:

```text
?night=off
```

명화 배경 끄기:

```text
?art=off
```

음악 끄기:

```text
?music=off
```

음악 재생을 시도하며 열기:

```text
?music=on
```

브라우저 정책상 소리가 나는 자동재생은 TV/모바일 브라우저에서 막힐 수 있습니다. 이 경우 `음악재생` 버튼을 한 번 눌러 주세요.

특정 음악으로 시작:

```text
?track=chopin-nocturne-loop
```

음악 모드 지정:

```text
?musicMode=playlist
```

사용 가능한 값은 `playlist`, `repeat-one`, `shuffle`입니다. 화면의 `음악선택` 패널에서도 `연속재생`, `한곡반복`, `무작위`를 전환할 수 있습니다.

타이머 기능 끄기:

```text
?timer=off
```

타이머 기본 프리셋 지정:

```text
?timerMinutes=25
```

알람 시간을 입력해 둔 상태로 열기:

```text
?alarm=07:30
```

URL 옵션은 값을 미리 채우기만 하며, 타이머 시작이나 알람 예약은 화면에서 버튼을 눌러야 합니다.

볼륨 지정:

```text
?volume=0.35
```

배경 변경 주기를 60초로 바꾸기:

```text
?artSeconds=60
```

여러 옵션을 같이 쓸 수 있습니다.

```text
?city=부산&lat=35.1796&lon=129.0756&seconds=off&artSeconds=60&track=gymnopedie-loop&musicMode=shuffle&timerMinutes=25&alarm=07:30&volume=0.4
```

## TV에서 쓰는 팁

- TV 브라우저에서 주소 접속 후 `전체화면` 버튼을 누르세요.
- 일부 TV는 브라우저 보안 정책 때문에 전체화면을 막을 수 있습니다.
- OLED TV라면 장시간 고정 화면 사용은 번인 위험이 있으니 주의하세요.
- 습도는 집 안의 실내 습도가 아니라 선택한 좌표의 실외 날씨 데이터입니다.
- 타이머 알림음은 사용자가 타이머/알람 버튼을 누른 뒤 Web Audio로 재생됩니다. 브라우저 정책상 첫 차임이 막히면 화면 알림은 계속 표시됩니다.
- 타이머/알람 알림은 60초 뒤 자동으로 조용해지고, 음악 재생 중에는 음악 볼륨을 잠시 낮춥니다.

## 사용 API

- 날씨: Open-Meteo Forecast API
- 명화 asset 생성: Cleveland Museum of Art Open Access API CC0 이미지
- 보조 후보: Metropolitan Museum of Art Open Access API, Art Institute of Chicago API 및 IIIF 이미지
- 음악 asset 생성: `scripts/generate_music_assets.py`로 만든 로컬 WAV 루프

브라우저에서 시계를 볼 때 명화는 저장소의 `assets/artworks/` 로컬 파일을 사용합니다. `scripts/fetch_art_assets.py`를 다시 실행하면 CC0/공개 도메인 명화 asset과 `assets/artworks.js` 매니페스트를 재생성할 수 있습니다.

브라우저에서 음악을 들을 때는 `assets/music/` 로컬 WAV 파일과 `assets/music.js` 매니페스트를 사용합니다. 클래식은 공개 도메인 선율을 단순 합성한 반복용 버전이고, 자연 소리는 절차적으로 생성한 빗소리/파도 소리입니다. 외부 음원 hotlink나 현대 녹음 파일 권리에 의존하지 않습니다.

두 API와 음악 asset 생성 모두 이 프로젝트에서는 별도 API 키 없이 사용할 수 있습니다.
