# API Index

전체 API 207개를 PDF 목차 순서대로 정리했습니다.

| No | API ID | API 명 | 대분류 | 중분류 | 페이지 | Method | URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [au10001](apis/001-au10001.md) | 접근토큰 발급 | OAuth 인증 | 접근토큰발급 | 7~8 | POST | /oauth2/token |
| 2 | [au10002](apis/002-au10002.md) | 접근토큰폐기 | OAuth 인증 | 접근토큰폐기 | 9~9 | POST | /oauth2/revoke |
| 3 | [ka00001](apis/003-ka00001.md) | 계좌번호조회 | 국내주식 | 계좌 | 10~10 | POST | /api/dostk/acnt |
| 4 | [ka00198](apis/004-ka00198.md) | 실시간종목조회순위 | 국내주식 | 종목정보 | 11~12 | POST | /api/dostk/stkinfo |
| 5 | [ka01690](apis/005-ka01690.md) | 일별잔고수익률 | 국내주식 | 계좌 | 13~14 | POST | /api/dostk/acnt |
| 6 | [ka10001](apis/006-ka10001.md) | 주식기본정보요청 | 국내주식 | 종목정보 | 15~17 | POST | /api/dostk/stkinfo |
| 7 | [ka10002](apis/007-ka10002.md) | 주식거래원요청 | 국내주식 | 종목정보 | 18~20 | POST | /api/dostk/stkinfo |
| 8 | [ka10003](apis/008-ka10003.md) | 체결정보요청 | 국내주식 | 종목정보 | 21~23 | POST | /api/dostk/stkinfo |
| 9 | [ka10004](apis/009-ka10004.md) | 주식호가요청 | 국내주식 | 시세 | 24~27 | POST | /api/dostk/mrkcond |
| 10 | [ka10005](apis/010-ka10005.md) | 주식일주월시분요청 | 국내주식 | 시세 | 28~30 | POST | /api/dostk/mrkcond |
| 11 | [ka10006](apis/011-ka10006.md) | 주식시분요청 | 국내주식 | 시세 | 31~32 | POST | /api/dostk/mrkcond |
| 12 | [ka10007](apis/012-ka10007.md) | 시세표성정보요청 | 국내주식 | 시세 | 33~38 | POST | /api/dostk/mrkcond |
| 13 | [ka10008](apis/013-ka10008.md) | 주식외국인종목별매매동향 | 국내주식 | 기관/외국인 | 39~41 | POST | /api/dostk/frgnistt |
| 14 | [ka10009](apis/014-ka10009.md) | 주식기관요청 | 국내주식 | 기관/외국인 | 42~43 | POST | /api/dostk/frgnistt |
| 15 | [ka10010](apis/015-ka10010.md) | 업종프로그램요청 | 국내주식 | 업종 | 44~45 | POST | /api/dostk/sect |
| 16 | [ka10011](apis/016-ka10011.md) | 신주인수권전체시세요청 | 국내주식 | 시세 | 46~47 | POST | /api/dostk/mrkcond |
| 17 | [ka10013](apis/017-ka10013.md) | 신용매매동향요청 | 국내주식 | 종목정보 | 48~50 | POST | /api/dostk/stkinfo |
| 18 | [ka10014](apis/018-ka10014.md) | 공매도추이요청 | 국내주식 | 공매도 | 51~53 | POST | /api/dostk/shsa |
| 19 | [ka10015](apis/019-ka10015.md) | 일별거래상세요청 | 국내주식 | 종목정보 | 54~57 | POST | /api/dostk/stkinfo |
| 20 | [ka10016](apis/020-ka10016.md) | 신고저가요청 | 국내주식 | 종목정보 | 58~60 | POST | /api/dostk/stkinfo |
| 21 | [ka10017](apis/021-ka10017.md) | 상하한가요청 | 국내주식 | 종목정보 | 61~63 | POST | /api/dostk/stkinfo |
| 22 | [ka10018](apis/022-ka10018.md) | 고저가근접요청 | 국내주식 | 종목정보 | 64~66 | POST | /api/dostk/stkinfo |
| 23 | [ka10019](apis/023-ka10019.md) | 가격급등락요청 | 국내주식 | 종목정보 | 67~69 | POST | /api/dostk/stkinfo |
| 24 | [ka10020](apis/024-ka10020.md) | 호가잔량상위요청 | 국내주식 | 순위정보 | 70~72 | POST | /api/dostk/rkinfo |
| 25 | [ka10021](apis/025-ka10021.md) | 호가잔량급증요청 | 국내주식 | 순위정보 | 73~74 | POST | /api/dostk/rkinfo |
| 26 | [ka10022](apis/026-ka10022.md) | 잔량율급증요청 | 국내주식 | 순위정보 | 75~76 | POST | /api/dostk/rkinfo |
| 27 | [ka10023](apis/027-ka10023.md) | 거래량급증요청 | 국내주식 | 순위정보 | 77~79 | POST | /api/dostk/rkinfo |
| 28 | [ka10024](apis/028-ka10024.md) | 거래량갱신요청 | 국내주식 | 종목정보 | 80~81 | POST | /api/dostk/stkinfo |
| 29 | [ka10025](apis/029-ka10025.md) | 매물대집중요청 | 국내주식 | 종목정보 | 82~84 | POST | /api/dostk/stkinfo |
| 30 | [ka10026](apis/030-ka10026.md) | 고저PER요청 | 국내주식 | 종목정보 | 85~86 | POST | /api/dostk/stkinfo |
| 31 | [ka10027](apis/031-ka10027.md) | 전일대비등락률상위요청 | 국내주식 | 순위정보 | 87~89 | POST | /api/dostk/rkinfo |
| 32 | [ka10028](apis/032-ka10028.md) | 시가대비등락률요청 | 국내주식 | 종목정보 | 90~92 | POST | /api/dostk/stkinfo |
| 33 | [ka10029](apis/033-ka10029.md) | 예상체결등락률상위요청 | 국내주식 | 순위정보 | 93~95 | POST | /api/dostk/rkinfo |
| 34 | [ka10030](apis/034-ka10030.md) | 당일거래량상위요청 | 국내주식 | 순위정보 | 96~98 | POST | /api/dostk/rkinfo |
| 35 | [ka10031](apis/035-ka10031.md) | 전일거래량상위요청 | 국내주식 | 순위정보 | 99~101 | POST | /api/dostk/rkinfo |
| 36 | [ka10032](apis/036-ka10032.md) | 거래대금상위요청 | 국내주식 | 순위정보 | 102~103 | POST | /api/dostk/rkinfo |
| 37 | [ka10033](apis/037-ka10033.md) | 신용비율상위요청 | 국내주식 | 순위정보 | 104~106 | POST | /api/dostk/rkinfo |
| 38 | [ka10034](apis/038-ka10034.md) | 외인기간별매매상위요청 | 국내주식 | 순위정보 | 107~108 | POST | /api/dostk/rkinfo |
| 39 | [ka10035](apis/039-ka10035.md) | 외인연속순매매상위요청 | 국내주식 | 순위정보 | 109~111 | POST | /api/dostk/rkinfo |
| 40 | [ka10036](apis/040-ka10036.md) | 외인한도소진율증가상위 | 국내주식 | 순위정보 | 112~113 | POST | /api/dostk/rkinfo |
| 41 | [ka10037](apis/041-ka10037.md) | 외국계창구매매상위요청 | 국내주식 | 순위정보 | 114~116 | POST | /api/dostk/rkinfo |
| 42 | [ka10038](apis/042-ka10038.md) | 종목별증권사순위요청 | 국내주식 | 순위정보 | 117~118 | POST | /api/dostk/rkinfo |
| 43 | [ka10039](apis/043-ka10039.md) | 증권사별매매상위요청 | 국내주식 | 순위정보 | 119~120 | POST | /api/dostk/rkinfo |
| 44 | [ka10040](apis/044-ka10040.md) | 당일주요거래원요청 | 국내주식 | 순위정보 | 121~123 | POST | /api/dostk/rkinfo |
| 45 | [ka10042](apis/045-ka10042.md) | 순매수거래원순위요청 | 국내주식 | 순위정보 | 124~125 | POST | /api/dostk/rkinfo |
| 46 | [ka10043](apis/046-ka10043.md) | 거래원매물대분석요청 | 국내주식 | 종목정보 | 126~128 | POST | /api/dostk/stkinfo |
| 47 | [ka10044](apis/047-ka10044.md) | 일별기관매매종목요청 | 국내주식 | 시세 | 129~130 | POST | /api/dostk/mrkcond |
| 48 | [ka10045](apis/048-ka10045.md) | 종목별기관매매추이요청 | 국내주식 | 시세 | 131~132 | POST | /api/dostk/mrkcond |
| 49 | [ka10046](apis/049-ka10046.md) | 체결강도추이시간별요청 | 국내주식 | 시세 | 133~134 | POST | /api/dostk/mrkcond |
| 50 | [ka10047](apis/050-ka10047.md) | 체결강도추이일별요청 | 국내주식 | 시세 | 135~136 | POST | /api/dostk/mrkcond |
| 51 | [ka10048](apis/051-ka10048.md) | ELW일별민감도지표요청 | 국내주식 | ELW | 137~139 | POST | /api/dostk/elw |
| 52 | [ka10050](apis/052-ka10050.md) | ELW민감도지표요청 | 국내주식 | ELW | 140~141 | POST | /api/dostk/elw |
| 53 | [ka10051](apis/053-ka10051.md) | 업종별투자자순매수요청 | 국내주식 | 업종 | 142~144 | POST | /api/dostk/sect |
| 54 | [ka10052](apis/054-ka10052.md) | 거래원순간거래량요청 | 국내주식 | 종목정보 | 145~146 | POST | /api/dostk/stkinfo |
| 55 | [ka10053](apis/055-ka10053.md) | 당일상위이탈원요청 | 국내주식 | 순위정보 | 147~148 | POST | /api/dostk/rkinfo |
| 56 | [ka10054](apis/056-ka10054.md) | 변동성완화장치발동종목요청 | 국내주식 | 종목정보 | 149~151 | POST | /api/dostk/stkinfo |
| 57 | [ka10055](apis/057-ka10055.md) | 당일전일체결량요청 | 국내주식 | 종목정보 | 152~153 | POST | /api/dostk/stkinfo |
| 58 | [ka10058](apis/058-ka10058.md) | 투자자별일별매매종목요청 | 국내주식 | 종목정보 | 154~155 | POST | /api/dostk/stkinfo |
| 59 | [ka10059](apis/059-ka10059.md) | 종목별투자자기관별요청 | 국내주식 | 종목정보 | 156~158 | POST | /api/dostk/stkinfo |
| 60 | [ka10060](apis/060-ka10060.md) | 종목별투자자기관별차트요청 | 국내주식 | 차트 | 159~161 | POST | /api/dostk/chart |
| 61 | [ka10061](apis/061-ka10061.md) | 종목별투자자기관별합계요청 | 국내주식 | 종목정보 | 162~163 | POST | /api/dostk/stkinfo |
| 62 | [ka10062](apis/062-ka10062.md) | 동일순매매순위요청 | 국내주식 | 순위정보 | 164~165 | POST | /api/dostk/rkinfo |
| 63 | [ka10063](apis/063-ka10063.md) | 장중투자자별매매요청 | 국내주식 | 시세 | 166~168 | POST | /api/dostk/mrkcond |
| 64 | [ka10064](apis/064-ka10064.md) | 장중투자자별매매차트요청 | 국내주식 | 차트 | 169~170 | POST | /api/dostk/chart |
| 65 | [ka10065](apis/065-ka10065.md) | 장중투자자별매매상위요청 | 국내주식 | 순위정보 | 171~172 | POST | /api/dostk/rkinfo |
| 66 | [ka10066](apis/066-ka10066.md) | 장마감후투자자별매매요청 | 국내주식 | 시세 | 173~175 | POST | /api/dostk/mrkcond |
| 67 | [ka10068](apis/067-ka10068.md) | 대차거래추이요청 | 국내주식 | 대차거래 | 176~177 | POST | /api/dostk/slb |
| 68 | [ka10069](apis/068-ka10069.md) | 대차거래상위10종목요청 | 국내주식 | 대차거래 | 178~179 | POST | /api/dostk/slb |
| 69 | [ka10072](apis/069-ka10072.md) | 일자별종목별실현손익요청_일자 | 국내주식 | 계좌 | 180~181 | POST | /api/dostk/acnt |
| 70 | [ka10073](apis/070-ka10073.md) | 일자별종목별실현손익요청_기간 | 국내주식 | 계좌 | 182~184 | POST | /api/dostk/acnt |
| 71 | [ka10074](apis/071-ka10074.md) | 일자별실현손익요청 | 국내주식 | 계좌 | 185~186 | POST | /api/dostk/acnt |
| 72 | [ka10075](apis/072-ka10075.md) | 미체결요청 | 국내주식 | 계좌 | 187~189 | POST | /api/dostk/acnt |
| 73 | [ka10076](apis/073-ka10076.md) | 체결요청 | 국내주식 | 계좌 | 190~192 | POST | /api/dostk/acnt |
| 74 | [ka10077](apis/074-ka10077.md) | 당일실현손익상세요청 | 국내주식 | 계좌 | 193~194 | POST | /api/dostk/acnt |
| 75 | [ka10078](apis/075-ka10078.md) | 증권사별종목매매동향요청 | 국내주식 | 시세 | 195~196 | POST | /api/dostk/mrkcond |
| 76 | [ka10079](apis/076-ka10079.md) | 주식틱차트조회요청 | 국내주식 | 차트 | 197~198 | POST | /api/dostk/chart |
| 77 | [ka10080](apis/077-ka10080.md) | 주식분봉차트조회요청 | 국내주식 | 차트 | 199~200 | POST | /api/dostk/chart |
| 78 | [ka10081](apis/078-ka10081.md) | 주식일봉차트조회요청 | 국내주식 | 차트 | 201~202 | POST | /api/dostk/chart |
| 79 | [ka10082](apis/079-ka10082.md) | 주식주봉차트조회요청 | 국내주식 | 차트 | 203~204 | POST | /api/dostk/chart |
| 80 | [ka10083](apis/080-ka10083.md) | 주식월봉차트조회요청 | 국내주식 | 차트 | 205~206 | POST | /api/dostk/chart |
| 81 | [ka10084](apis/081-ka10084.md) | 당일전일체결요청 | 국내주식 | 종목정보 | 207~208 | POST | /api/dostk/stkinfo |
| 82 | [ka10085](apis/082-ka10085.md) | 계좌수익률요청 | 국내주식 | 계좌 | 209~211 | POST | /api/dostk/acnt |
| 83 | [ka10086](apis/083-ka10086.md) | 일별주가요청 | 국내주식 | 시세 | 212~214 | POST | /api/dostk/mrkcond |
| 84 | [ka10087](apis/084-ka10087.md) | 시간외단일가요청 | 국내주식 | 시세 | 215~218 | POST | /api/dostk/mrkcond |
| 85 | [ka10088](apis/085-ka10088.md) | 미체결 분할주문 상세 | 국내주식 | 계좌 | 219~220 | POST | /api/dostk/acnt |
| 86 | [ka10094](apis/086-ka10094.md) | 주식년봉차트조회요청 | 국내주식 | 차트 | 221~222 | POST | /api/dostk/chart |
| 87 | [ka10095](apis/087-ka10095.md) | 관심종목정보요청 | 국내주식 | 종목정보 | 223~226 | POST | /api/dostk/stkinfo |
| 88 | [ka10098](apis/088-ka10098.md) | 시간외단일가등락율순위요청 | 국내주식 | 순위정보 | 227~228 | POST | /api/dostk/rkinfo |
| 89 | [ka10099](apis/089-ka10099.md) | 종목정보 리스트 | 국내주식 | 종목정보 | 229~231 | POST | /api/dostk/stkinfo |
| 90 | [ka10100](apis/090-ka10100.md) | 종목정보 조회 | 국내주식 | 종목정보 | 232~233 | POST | /api/dostk/stkinfo |
| 91 | [ka10101](apis/091-ka10101.md) | 업종코드 리스트 | 국내주식 | 종목정보 | 234~235 | POST | /api/dostk/stkinfo |
| 92 | [ka10102](apis/092-ka10102.md) | 회원사 리스트 | 국내주식 | 종목정보 | 236~237 | POST | /api/dostk/stkinfo |
| 93 | [ka10131](apis/093-ka10131.md) | 기관외국인연속매매현황요청 | 국내주식 | 기관/외국인 | 238~240 | POST | /api/dostk/frgnistt |
| 94 | [ka10170](apis/094-ka10170.md) | 당일매매일지요청 | 국내주식 | 계좌 | 241~242 | POST | /api/dostk/acnt |
| 95 | [ka10171](apis/095-ka10171.md) | 조건검색 목록조회 | 국내주식 | 조건검색 | 243~244 | POST | /api/dostk/websocket |
| 96 | [ka10172](apis/096-ka10172.md) | 조건검색 요청 일반 | 국내주식 | 조건검색 | 245~247 | POST | /api/dostk/websocket |
| 97 | [ka10173](apis/097-ka10173.md) | 조건검색 요청 실시간 | 국내주식 | 조건검색 | 248~250 | POST | /api/dostk/websocket |
| 98 | [ka10174](apis/098-ka10174.md) | 조건검색 실시간 해제 | 국내주식 | 조건검색 | 251~252 | POST | /api/dostk/websocket |
| 99 | [ka20001](apis/099-ka20001.md) | 업종현재가요청 | 국내주식 | 업종 | 253~255 | POST | /api/dostk/sect |
| 100 | [ka20002](apis/100-ka20002.md) | 업종별주가요청 | 국내주식 | 업종 | 256~258 | POST | /api/dostk/sect |
| 101 | [ka20003](apis/101-ka20003.md) | 전업종지수요청 | 국내주식 | 업종 | 259~260 | POST | /api/dostk/sect |
| 102 | [ka20004](apis/102-ka20004.md) | 업종틱차트조회요청 | 국내주식 | 차트 | 261~262 | POST | /api/dostk/chart |
| 103 | [ka20005](apis/103-ka20005.md) | 업종분봉조회요청 | 국내주식 | 차트 | 263~264 | POST | /api/dostk/chart |
| 104 | [ka20006](apis/104-ka20006.md) | 업종일봉조회요청 | 국내주식 | 차트 | 265~266 | POST | /api/dostk/chart |
| 105 | [ka20007](apis/105-ka20007.md) | 업종주봉조회요청 | 국내주식 | 차트 | 267~268 | POST | /api/dostk/chart |
| 106 | [ka20008](apis/106-ka20008.md) | 업종월봉조회요청 | 국내주식 | 차트 | 269~270 | POST | /api/dostk/chart |
| 107 | [ka20009](apis/107-ka20009.md) | 업종현재가일별요청 | 국내주식 | 업종 | 271~273 | POST | /api/dostk/sect |
| 108 | [ka20019](apis/108-ka20019.md) | 업종년봉조회요청 | 국내주식 | 차트 | 274~275 | POST | /api/dostk/chart |
| 109 | [ka20068](apis/109-ka20068.md) | 대차거래추이요청(종목별) | 국내주식 | 대차거래 | 276~277 | POST | /api/dostk/slb |
| 110 | [ka30001](apis/110-ka30001.md) | ELW가격급등락요청 | 국내주식 | ELW | 278~279 | POST | /api/dostk/elw |
| 111 | [ka30002](apis/111-ka30002.md) | 거래원별ELW순매매상위요청 | 국내주식 | ELW | 280~281 | POST | /api/dostk/elw |
| 112 | [ka30003](apis/112-ka30003.md) | ELWLP보유일별추이요청 | 국내주식 | ELW | 282~283 | POST | /api/dostk/elw |
| 113 | [ka30004](apis/113-ka30004.md) | ELW괴리율요청 | 국내주식 | ELW | 284~286 | POST | /api/dostk/elw |
| 114 | [ka30005](apis/114-ka30005.md) | ELW조건검색요청 | 국내주식 | ELW | 287~289 | POST | /api/dostk/elw |
| 115 | [ka30009](apis/115-ka30009.md) | ELW등락율순위요청 | 국내주식 | ELW | 290~291 | POST | /api/dostk/elw |
| 116 | [ka30010](apis/116-ka30010.md) | ELW잔량순위요청 | 국내주식 | ELW | 292~293 | POST | /api/dostk/elw |
| 117 | [ka30011](apis/117-ka30011.md) | ELW근접율요청 | 국내주식 | ELW | 294~295 | POST | /api/dostk/elw |
| 118 | [ka30012](apis/118-ka30012.md) | ELW종목상세정보요청 | 국내주식 | ELW | 296~299 | POST | /api/dostk/elw |
| 119 | [ka40001](apis/119-ka40001.md) | ETF수익율요청 | 국내주식 | ETF | 300~301 | POST | /api/dostk/etf |
| 120 | [ka40002](apis/120-ka40002.md) | ETF종목정보요청 | 국내주식 | ETF | 302~303 | POST | /api/dostk/etf |
| 121 | [ka40003](apis/121-ka40003.md) | ETF일별추이요청 | 국내주식 | ETF | 304~305 | POST | /api/dostk/etf |
| 122 | [ka40004](apis/122-ka40004.md) | ETF전체시세요청 | 국내주식 | ETF | 306~308 | POST | /api/dostk/etf |
| 123 | [ka40006](apis/123-ka40006.md) | ETF시간대별추이요청 | 국내주식 | ETF | 309~310 | POST | /api/dostk/etf |
| 124 | [ka40007](apis/124-ka40007.md) | ETF시간대별체결요청 | 국내주식 | ETF | 311~312 | POST | /api/dostk/etf |
| 125 | [ka40008](apis/125-ka40008.md) | ETF일자별체결요청 | 국내주식 | ETF | 313~314 | POST | /api/dostk/etf |
| 126 | [ka40009](apis/126-ka40009.md) | ETF시간대별NAV현황 | 국내주식 | ETF | 315~316 | POST | /api/dostk/etf |
| 127 | [ka40010](apis/127-ka40010.md) | ETF시간대별수급현황 | 국내주식 | ETF | 317~318 | POST | /api/dostk/etf |
| 128 | [ka50010](apis/128-ka50010.md) | 금현물체결추이 | 국내주식 | 시세 | 319~320 | POST | /api/dostk/mrkcond |
| 129 | [ka50012](apis/129-ka50012.md) | 금현물일별추이 | 국내주식 | 시세 | 321~322 | POST | /api/dostk/mrkcond |
| 130 | [ka50079](apis/130-ka50079.md) | 금현물틱차트조회요청 | 국내주식 | 차트 | 323~324 | POST | /api/dostk/chart |
| 131 | [ka50080](apis/131-ka50080.md) | 금현물분봉차트조회요청 | 국내주식 | 차트 | 325~326 | POST | /api/dostk/chart |
| 132 | [ka50081](apis/132-ka50081.md) | 금현물일봉차트조회요청 | 국내주식 | 차트 | 327~328 | POST | /api/dostk/chart |
| 133 | [ka50082](apis/133-ka50082.md) | 금현물주봉차트조회요청 | 국내주식 | 차트 | 329~330 | POST | /api/dostk/chart |
| 134 | [ka50083](apis/134-ka50083.md) | 금현물월봉차트조회요청 | 국내주식 | 차트 | 331~332 | POST | /api/dostk/chart |
| 135 | [ka50087](apis/135-ka50087.md) | 금현물예상체결 | 국내주식 | 시세 | 333~334 | POST | /api/dostk/mrkcond |
| 136 | [ka50091](apis/136-ka50091.md) | 금현물당일틱차트조회요청 | 국내주식 | 차트 | 335~336 | POST | /api/dostk/chart |
| 137 | [ka50092](apis/137-ka50092.md) | 금현물당일분봉차트조회요청 | 국내주식 | 차트 | 337~338 | POST | /api/dostk/chart |
| 138 | [ka50100](apis/138-ka50100.md) | 금현물 시세정보 | 국내주식 | 시세 | 339~340 | POST | /api/dostk/mrkcond |
| 139 | [ka50101](apis/139-ka50101.md) | 금현물 호가 | 국내주식 | 시세 | 341~342 | POST | /api/dostk/mrkcond |
| 140 | [ka52301](apis/140-ka52301.md) | 금현물투자자현황 | 국내주식 | 기관/외국인 | 343~345 | POST | /api/dostk/frgnistt |
| 141 | [ka90001](apis/141-ka90001.md) | 테마그룹별요청 | 국내주식 | 테마 | 346~347 | POST | /api/dostk/thme |
| 142 | [ka90002](apis/142-ka90002.md) | 테마구성종목요청 | 국내주식 | 테마 | 348~350 | POST | /api/dostk/thme |
| 143 | [ka90003](apis/143-ka90003.md) | 프로그램순매수상위50요청 | 국내주식 | 종목정보 | 351~352 | POST | /api/dostk/stkinfo |
| 144 | [ka90004](apis/144-ka90004.md) | 종목별프로그램매매현황요청 | 국내주식 | 종목정보 | 353~355 | POST | /api/dostk/stkinfo |
| 145 | [ka90005](apis/145-ka90005.md) | 프로그램매매추이요청 시간대별 | 국내주식 | 시세 | 356~358 | POST | /api/dostk/mrkcond |
| 146 | [ka90006](apis/146-ka90006.md) | 프로그램매매차익잔고추이요청 | 국내주식 | 시세 | 359~360 | POST | /api/dostk/mrkcond |
| 147 | [ka90007](apis/147-ka90007.md) | 프로그램매매누적추이요청 | 국내주식 | 시세 | 361~362 | POST | /api/dostk/mrkcond |
| 148 | [ka90008](apis/148-ka90008.md) | 종목시간별프로그램매매추이요청 | 국내주식 | 시세 | 363~365 | POST | /api/dostk/mrkcond |
| 149 | [ka90009](apis/149-ka90009.md) | 외국인기관매매상위요청 | 국내주식 | 순위정보 | 366~368 | POST | /api/dostk/rkinfo |
| 150 | [ka90010](apis/150-ka90010.md) | 프로그램매매추이요청 일자별 | 국내주식 | 시세 | 369~371 | POST | /api/dostk/mrkcond |
| 151 | [ka90012](apis/151-ka90012.md) | 대차거래내역요청 | 국내주식 | 대차거래 | 372~373 | POST | /api/dostk/slb |
| 152 | [ka90013](apis/152-ka90013.md) | 종목일별프로그램매매추이요청 | 국내주식 | 시세 | 374~376 | POST | /api/dostk/mrkcond |
| 153 | [kt00001](apis/153-kt00001.md) | 예수금상세현황요청 | 국내주식 | 계좌 | 377~381 | POST | /api/dostk/acnt |
| 154 | [kt00002](apis/154-kt00002.md) | 일별추정예탁자산현황요청 | 국내주식 | 계좌 | 382~383 | POST | /api/dostk/acnt |
| 155 | [kt00003](apis/155-kt00003.md) | 추정자산조회요청 | 국내주식 | 계좌 | 384~384 | POST | /api/dostk/acnt |
| 156 | [kt00004](apis/156-kt00004.md) | 계좌평가현황요청 | 국내주식 | 계좌 | 385~387 | POST | /api/dostk/acnt |
| 157 | [kt00005](apis/157-kt00005.md) | 체결잔고요청 | 국내주식 | 계좌 | 388~390 | POST | /api/dostk/acnt |
| 158 | [kt00007](apis/158-kt00007.md) | 계좌별주문체결내역상세요청 | 국내주식 | 계좌 | 391~393 | POST | /api/dostk/acnt |
| 159 | [kt00008](apis/159-kt00008.md) | 계좌별익일결제예정내역요청 | 국내주식 | 계좌 | 394~395 | POST | /api/dostk/acnt |
| 160 | [kt00009](apis/160-kt00009.md) | 계좌별주문체결현황요청 | 국내주식 | 계좌 | 396~398 | POST | /api/dostk/acnt |
| 161 | [kt00010](apis/161-kt00010.md) | 주문인출가능금액요청 | 국내주식 | 계좌 | 399~401 | POST | /api/dostk/acnt |
| 162 | [kt00011](apis/162-kt00011.md) | 증거금율별주문가능수량조회요청 | 국내주식 | 계좌 | 402~404 | POST | /api/dostk/acnt |
| 163 | [kt00012](apis/163-kt00012.md) | 신용보증금율별주문가능수량조회요청 | 국내주식 | 계좌 | 405~407 | POST | /api/dostk/acnt |
| 164 | [kt00013](apis/164-kt00013.md) | 증거금세부내역조회요청 | 국내주식 | 계좌 | 408~410 | POST | /api/dostk/acnt |
| 165 | [kt00015](apis/165-kt00015.md) | 위탁종합거래내역요청 | 국내주식 | 계좌 | 411~414 | POST | /api/dostk/acnt |
| 166 | [kt00016](apis/166-kt00016.md) | 일별계좌수익률상세현황요청 | 국내주식 | 계좌 | 415~417 | POST | /api/dostk/acnt |
| 167 | [kt00017](apis/167-kt00017.md) | 계좌별당일현황요청 | 국내주식 | 계좌 | 418~419 | POST | /api/dostk/acnt |
| 168 | [kt00018](apis/168-kt00018.md) | 계좌평가잔고내역요청 | 국내주식 | 계좌 | 420~422 | POST | /api/dostk/acnt |
| 169 | [kt10000](apis/169-kt10000.md) | 주식 매수주문 | 국내주식 | 주문 | 423~424 | POST | /api/dostk/ordr |
| 170 | [kt10001](apis/170-kt10001.md) | 주식 매도주문 | 국내주식 | 주문 | 425~426 | POST | /api/dostk/ordr |
| 171 | [kt10002](apis/171-kt10002.md) | 주식 정정주문 | 국내주식 | 주문 | 427~428 | POST | /api/dostk/ordr |
| 172 | [kt10003](apis/172-kt10003.md) | 주식 취소주문 | 국내주식 | 주문 | 429~430 | POST | /api/dostk/ordr |
| 173 | [kt10006](apis/173-kt10006.md) | 신용 매수주문 | 국내주식 | 신용주문 | 431~432 | POST | /api/dostk/crdordr |
| 174 | [kt10007](apis/174-kt10007.md) | 신용 매도주문 | 국내주식 | 신용주문 | 433~434 | POST | /api/dostk/crdordr |
| 175 | [kt10008](apis/175-kt10008.md) | 신용 정정주문 | 국내주식 | 신용주문 | 435~436 | POST | /api/dostk/crdordr |
| 176 | [kt10009](apis/176-kt10009.md) | 신용 취소주문 | 국내주식 | 신용주문 | 437~438 | POST | /api/dostk/crdordr |
| 177 | [kt20016](apis/177-kt20016.md) | 신용융자 가능종목요청 | 국내주식 | 종목정보 | 439~440 | POST | /api/dostk/stkinfo |
| 178 | [kt20017](apis/178-kt20017.md) | 신용융자 가능문의 | 국내주식 | 종목정보 | 441~441 | POST | /api/dostk/stkinfo |
| 179 | [kt50000](apis/179-kt50000.md) | 금현물 매수주문 | 국내주식 | 주문 | 442~443 | POST | /api/dostk/ordr |
| 180 | [kt50001](apis/180-kt50001.md) | 금현물 매도주문 | 국내주식 | 주문 | 444~445 | POST | /api/dostk/ordr |
| 181 | [kt50002](apis/181-kt50002.md) | 금현물 정정주문 | 국내주식 | 주문 | 446~447 | POST | /api/dostk/ordr |
| 182 | [kt50003](apis/182-kt50003.md) | 금현물 취소주문 | 국내주식 | 주문 | 448~449 | POST | /api/dostk/ordr |
| 183 | [kt50020](apis/183-kt50020.md) | 금현물 잔고확인 | 국내주식 | 계좌 | 450~452 | POST | /api/dostk/acnt |
| 184 | [kt50021](apis/184-kt50021.md) | 금현물 예수금 | 국내주식 | 계좌 | 453~454 | POST | /api/dostk/acnt |
| 185 | [kt50030](apis/185-kt50030.md) | 금현물 주문체결전체조회 | 국내주식 | 계좌 | 455~457 | POST | /api/dostk/acnt |
| 186 | [kt50031](apis/186-kt50031.md) | 금현물 주문체결조회 | 국내주식 | 계좌 | 458~460 | POST | /api/dostk/acnt |
| 187 | [kt50032](apis/187-kt50032.md) | 금현물 거래내역조회 | 국내주식 | 계좌 | 461~463 | POST | /api/dostk/acnt |
| 188 | [kt50075](apis/188-kt50075.md) | 금현물 미체결조회 | 국내주식 | 계좌 | 464~466 | POST | /api/dostk/acnt |
| 189 | [00](apis/189-00.md) | 주문체결 | 국내주식 | 실시간시세 | 467~470 | POST | /api/dostk/websocket |
| 190 | [04](apis/190-04.md) | 잔고 | 국내주식 | 실시간시세 | 471~473 | POST | /api/dostk/websocket |
| 191 | [0A](apis/191-0A.md) | 주식기세 | 국내주식 | 실시간시세 | 474~476 | POST | /api/dostk/websocket |
| 192 | [0B](apis/192-0B.md) | 주식체결 | 국내주식 | 실시간시세 | 477~480 | POST | /api/dostk/websocket |
| 193 | [0C](apis/193-0C.md) | 주식우선호가 | 국내주식 | 실시간시세 | 481~482 | POST | /api/dostk/websocket |
| 194 | [0D](apis/194-0D.md) | 주식호가잔량 | 국내주식 | 실시간시세 | 483~491 | POST | /api/dostk/websocket |
| 195 | [0E](apis/195-0E.md) | 주식시간외호가 | 국내주식 | 실시간시세 | 492~493 | POST | /api/dostk/websocket |
| 196 | [0F](apis/196-0F.md) | 주식당일거래원 | 국내주식 | 실시간시세 | 494~497 | POST | /api/dostk/websocket |
| 197 | [0G](apis/197-0G.md) | ETF NAV | 국내주식 | 실시간시세 | 498~500 | POST | /api/dostk/websocket |
| 198 | [0H](apis/198-0H.md) | 주식예상체결 | 국내주식 | 실시간시세 | 501~502 | POST | /api/dostk/websocket |
| 199 | [0I](apis/199-0I.md) | 국제금환산가격 | 국내주식 | 실시간시세 | 503~504 | POST | /api/dostk/websocket |
| 200 | [0J](apis/200-0J.md) | 업종지수 | 국내주식 | 실시간시세 | 505~507 | POST | /api/dostk/websocket |
| 201 | [0U](apis/201-0U.md) | 업종등락 | 국내주식 | 실시간시세 | 508~510 | POST | /api/dostk/websocket |
| 202 | [0g](apis/202-0g.md) | 주식종목정보 | 국내주식 | 실시간시세 | 511~513 | POST | /api/dostk/websocket |
| 203 | [0m](apis/203-0m.md) | ELW 이론가 | 국내주식 | 실시간시세 | 514~516 | POST | /api/dostk/websocket |
| 204 | [0s](apis/204-0s.md) | 장시작시간 | 국내주식 | 실시간시세 | 517~519 | POST | /api/dostk/websocket |
| 205 | [0u](apis/205-0u.md) | ELW 지표 | 국내주식 | 실시간시세 | 520~521 | POST | /api/dostk/websocket |
| 206 | [0w](apis/206-0w.md) | 종목프로그램매매 | 국내주식 | 실시간시세 | 522~524 | POST | /api/dostk/websocket |
| 207 | [1h](apis/207-1h.md) | VI발동/해제 | 국내주식 | 실시간시세 | 525~527 | POST | /api/dostk/websocket |
