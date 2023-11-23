import sys
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def class_mapping(row):
    mappings = {'障害':0, 'G1': 10, 'G2': 9, 'G3': 8, '(L)': 7, 'オープン': 7,'OP': 7, '3勝': 6, '1600': 6, '2勝': 5, '1000': 5, '1勝': 4, '500': 4, '新馬': 3, '未勝利': 1}
    for key, value in mappings.items():
        if key in row:
            return value
    return 0


sex_mapping = {'牡':0, '牝': 1, 'セ': 2}
shiba_mapping = {'芝': 0, 'ダ': 1, '障': 2}
mawari_mapping = {'右': 0, '左': 1, '芝': 2, '直': 2}
baba_mapping = {'良': 0, '稍': 1, '重': 2, '不': 3}
tenki_mapping = {'晴': 0, '曇': 1, '小': 2, '雨': 3, '雪': 4}


PLACES = ["", "札幌", "函館", "福島", "新潟", "東京", "中山", "中京", "京都", "阪神", "小倉"]

def get_race(race_id):
    w = race_id[4] + race_id[5]
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # 以下のコマンドでHeadless Chromeのコンテナを起動しておく必要がある
    # docker run -d -p 4444:4444 -v /dev/shm:/dev/shm selenium/standalone-chrome:3.141.59-xenon
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        desired_capabilities=options.to_capabilities(),
        options=options,
    )

    base_url = "https://race.netkeiba.com"
    url=f"{base_url}/race/shutuba.html?race_id={race_id}&rf=race_list"
    driver.get(url)

    s = driver.find_element(By.CSS_SELECTOR, 'dd.Active').text
    date = datetime.strptime(s[:-3], '%m月%d日').replace(year=int(race_id[0:4]))
    print(date)

    title = driver.find_element(By.CLASS_NAME, 'RaceName').text
    horses = driver.find_elements(By.CLASS_NAME, 'HorseList')

    race_data01 = driver.find_element(By.CLASS_NAME, 'RaceData01').text.split('/')
    re_res1 = re.match(r'(.)(\d+)m \((左|右).*\)', race_data01[1].strip())

    clas = class_mapping(title)
    sur = re_res1.group(1)
    dis = int(re_res1.group(2))
    rou = re_res1.group(3)
    con = race_data01[3].strip()[-1]
    wed = race_data01[2].strip()[-1]
    detail = ""

    print(clas, sur, dis, rou, con, wed, detail)

    horse_urls = []
    race_data_all = []
    for horse in horses:

        td_list = horse.find_elements(By.TAG_NAME, 'td')

        horse_name = td_list[3].text
        jockey = td_list[6].text
        umaban = td_list[1].text
        odds = float(td_list[9].text)
        pas = ""
        chaku = ""

        weight, weight_dif = td_list[8].text.split('(')
        weight_dif = float(weight_dif.strip(')'))

        sex_age = td_list[4].text
        sex = sex_mapping[sex_age[0]]
        age = sex_age[1]
        kinryo = td_list[5].text
        last = ""
        pop = int(td_list[10].text)
        souha=""

        horse_url = td_list[3].find_element(By.TAG_NAME, 'a').get_property('href')
        horse_urls.append(horse_url)

        race_data = [
            race_id,
            umaban,
            horse_name,
            jockey,
            pop,#人気,
            odds,
            souha,
            pas,#通過順
            chaku,#着順
            weight,#体重
            weight_dif,#体重変化
            sex,
            age,
            kinryo,
            last,#上がり
            title,#レース名
            date,#日付
            detail,
            clas,
            shiba_mapping[sur],
            dis,#距離
            mawari_mapping[rou],
            baba_mapping[con],
            tenki_mapping[wed],
            w,#場
            PLACES[int(w)]]
        race_data_all.append(race_data)

    colmuns = ['race_id','馬番','馬','騎手','人気','オッズ','走破時間','通過順','着順','体重','体重変化','性','齢','斤量','上がり','レース名','日付','開催','クラス','芝・ダート','距離','回り','馬場','天気','場id','場名']

    df = pd.DataFrame(race_data_all, columns=colmuns)
    df['日付'] = pd.to_datetime(df['日付'])
    df['距離'] = df['距離'].astype(int)

    return df, horse_urls

def get_past_races(url_list, cutoff_date):
    all_results = []  # 全てレース結果を保存するためのリスト

    # cutoff_date = datetime.strptime('2023/05/27', '%Y/%m/%d')  # 特定の日付を指定
    # 現在の日付を取得
    # now = datetime.now()
    # cutoff_date を datetime 型に変換
    # cutoff_date = datetime.strptime(now.strftime('%Y/%m/%d'), '%Y/%m/%d')
    for url in url_list:
        results = []  # 馬単位のレース結果を保存するためのリスト
        response = requests.get(url)

        # ステータスコードが200以外の場合はエラーが発生したとみなし、処理をスキップ
        if response.status_code != 200:
            print(f"Error occurred while fetching data from {url}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")

        # テーブルを指定
        table = soup.find("table", {"class": "db_h_race_results nk_tb_common"})

        # テーブル内の全ての行を取得
        rows = table.find_all("tr")

        # 各行から必要な情報を取り出し
        for i, row in enumerate(rows[1:], start=1):# ヘッダ行をスキップ
            cols = row.find_all("td")

            # 日付を解析
            str_date = cols[0].text.strip()
            date = datetime.strptime(str_date, '%Y/%m/%d')

            # 特定の日付より前のデータのみを取得
            if date < cutoff_date:
                # 取得したいデータの位置を指定し取得
                #体重
                horse_weight = cols[23].text.strip()
                weight = 0
                weight_dif = 0
                try:
                    weight = int(horse_weight.split("(")[0])
                    weight_dif = int(horse_weight.split("(")[1][0:-1])
                except:
                    weight = ''
                    weight_dif = ''
                weight = weight
                weight_dif = weight_dif
                #上がり
                up = cols[22].text.strip()
                #通過順
                through = cols[20].text.strip()
                try:
                    numbers = list(map(int, through.split('-')))
                    through = sum(numbers) / len(numbers)
                except ValueError:
                    through = ''
                #着順
                order_of_finish = cols[11].text.strip()
                try:
                    order_of_finish = str(int(order_of_finish))
                except ValueError:
                    order_of_finish = ""
                #馬番
                past_umaban = cols[8].text.strip()
                #騎手
                past_kishu = cols[12].text.strip()
                #斤量
                past_kinryo = cols[13].text.strip()
                #距離
                distance = cols[14].text.strip()
                #芝・ダート
                track = distance[0]
                shiba_mapping = {'芝': 0, 'ダ': 1, '障': 2}
                track = shiba_mapping.get(track)
                #距離
                distance = distance[1:]
                #レース名
                race_name = cols[4].text.strip()
                race_rank = class_mapping(race_name)
                #タイム
                time = cols[17].text.strip()
                try:
                    time = float(time.split(':')[0]) * 60 + sum(float(x) / 10**i for i, x in enumerate(time.split(':')[1].split('.')))
                except:
                    time = ''
                #天気
                weather = cols[2].text.strip()
                tenki_mapping = {'晴': 0, '曇': 1, '小': 2, '雨': 3, '雪': 4}
                weather = tenki_mapping.get(weather)
                #オッズ
                odds = cols[9].text.strip()
                track_condition = cols[15].text.strip()
                #馬場状態
                baba_mapping = {'良': 0, '稍': 1, '重': 2, '不': 3}
                track_condition = baba_mapping.get(track_condition)

                result = [str_date,past_umaban,past_kishu,past_kinryo, odds, weight, weight_dif, up, through, order_of_finish, distance, race_rank, time, track, weather, track_condition,"",""]
                results.append(result)

                # 5行取得したら終了
                if len(results) >= 5:
                    flattened_results = []
                    for r in results:
                        flattened_results.extend(r)

                    all_results.append(flattened_results)
                    break

                # 最終ループを判定
                if i == len(rows[1:]):
                    if results:  # resultsが空でない場合
                        flattened_results = []
                        for r in results:
                            flattened_results.extend(r)
                        all_results.append(flattened_results)


    columns = ['日付1', '馬番1', '騎手1', '斤量1', 'オッズ1', '体重1', '体重変化1', '上がり1', '通過順1', '着順1', '距離1', 'クラス1', '走破時間1', '芝・ダート1', '天気1', '馬場1', '距離差1', '日付差1', '日付2', '馬番2', '騎手2', '斤量2', 'オッズ2', '体重2', '体重変化2', '上がり2', '通過順2', '着順2', '距離2', 'クラス2', '走破時間2', '芝・ダート2', '天気2', '馬場2', '距離差2', '日付差2', '日付3', '馬番3', '騎手3', '斤量3', 'オッズ3', '体重3', '体重変化3', '上がり3', '通過順3', '着順3', '距離3', 'クラス3', '走破時間3', '芝・ダート3', '天気3', '馬場3', '距離差3', '日付差3', '日付4', '馬番4', '騎手4', '斤量4', 'オッズ4', '体重4', '体重変化4', '上がり4', '通過順4', '着順4', '距離4', 'クラス4', '走破時間4', '芝・ダート4', '天気4', '馬場4', '距離差4', '日付差4', '日付5', '馬番5', '騎手5', '斤量5', 'オッズ5', '体重5', '体重変化5', '上がり5', '通過順5', '着順5', '距離5', 'クラス5', '走破時間5', '芝・ダート5', '天気5', '馬場5',]


    def pad_null(xs):
        res = []
        for i in range(len(columns)):
            if i < len(xs):
                res.append(xs[i])
            else:
                res.append(None)
        return res

    results = []
    for result in all_results:
        results.append(pad_null(result))


    df = pd.DataFrame(results, columns=columns)
    
    df['日付1'] = pd.to_datetime(df['日付1'])
    df['距離1'] = df['距離1'].astype(int)
    return df

if __name__ == '__main__':
    assert(len(sys.argv) >= 2)
    race_id = sys.argv[1]

    # レースデータ取得
    race_data, urls_list = get_race(race_id)
    race_date = race_data['日付'][0]
    # 各馬の過去の5走を取得
    past_data = get_past_races(urls_list, race_date)

    dist_dif = (race_data['距離'] - past_data['距離1'])
    days_dif = (race_data['日付'] - past_data['日付1']).dt.days
    tmp = pd.concat([dist_dif, days_dif], axis=1, keys=['距離差', '日付差'])

    # 出力
    df = pd.concat([race_data, tmp, past_data], axis=1)
    df.to_csv("race_data/tmp.csv", index=False)
