import os
import random
import time
from pathlib import Path

import streamlit as st
from openai import OpenAI
from PIL import Image


OPENAI_API_KEY = ""

st.set_page_config(
    page_title="Tarot Reflection",
    page_icon="*",
    layout="centered",
)

BASE_DIR = Path(__file__).parent
CARDS_DIR = BASE_DIR / "cards_tiny"


TAROT_CARDS = [
    {"number": 0, "name_en": "THE FOOL", "name_ja": "愚者", "image": "00_fool.jpg", "upright": "始まり、無垢、未知への一歩、自由、衝動、まだ形になる前の可能性", "reversed": "無計画さ、足元の不安、衝動に流されること、始める前のためらい、自由への怖さ"},
    {"number": 1, "name_en": "THE MAGUS", "name_ja": "魔術師", "image": "01_magus.jpg", "upright": "意志、創造、言葉にする力、始動、手元にある道具を使うこと", "reversed": "言葉だけが先に立つこと、力の使い方への迷い、準備不足、自分の道具を信じきれないこと"},
    {"number": 2, "name_en": "THE HIGH PRIESTESS", "name_ja": "女教皇", "image": "02_high_priestess.jpg", "upright": "沈黙、直感、まだ言葉にならない知、隠された本音、内側の水面", "reversed": "感覚を疑いすぎること、沈黙の中に閉じこもること、見ないふりをしている本音"},
    {"number": 3, "name_en": "THE EMPRESS", "name_ja": "女帝", "image": "03_empress.jpg", "upright": "豊かさ、育つもの、受容、身体感覚、愛情、自然な実り", "reversed": "与えすぎ、受け取り下手、育つ前に急かすこと、満たされなさを埋めようとすること"},
    {"number": 4, "name_en": "THE EMPEROR", "name_ja": "皇帝", "image": "04_emperor.jpg", "upright": "秩序、父性、責任、構造、守る力、揺るがない土台", "reversed": "支配、頑なさ、責任の重さ、守るために感情を閉じること、強くあろうとしすぎること"},
    {"number": 5, "name_en": "THE HIEROPHANT", "name_ja": "教皇", "image": "05_hierophant.jpg", "upright": "制度、信仰、教え、伝統、形式、受け継がれるもの", "reversed": "形骸化したルール、外側の正しさへの違和感、自分の信念と制度のずれ"},
    {"number": 6, "name_en": "THE LOVERS", "name_ja": "恋人", "image": "06_lovers.jpg", "upright": "選択、関係性、惹かれ合い、価値観、他者を通して自分を知ること", "reversed": "選べなさ、依存、関係の中で自分を見失うこと、価値観のずれへの違和感"},
    {"number": 7, "name_en": "THE CHARIOT", "name_ja": "戦車", "image": "07_chariot.jpg", "upright": "前進、意志、制御、葛藤を抱えたまま進む力、勝利への集中", "reversed": "空回り、焦り、進みたいのに方向が定まらないこと、制御しようとしすぎること"},
    {"number": 8, "name_en": "STRENGTH", "name_ja": "力", "image": "08_strength.jpg", "upright": "やさしい強さ、本能との和解、忍耐、内側から湧く力、支配しない勇気", "reversed": "自分の本能を怖がること、弱さを責めること、優しさを出せないほどの緊張"},
    {"number": 9, "name_en": "THE HERMIT", "name_ja": "隠者", "image": "09_hermit.jpg", "upright": "孤独、探求、内省、静かな知恵、自分だけの灯り、距離を置くこと", "reversed": "孤立、考えすぎ、外に出る怖さ、自分の中だけで答えを閉じてしまうこと"},
    {"number": 10, "name_en": "WHEEL OF FORTUNE", "name_ja": "運命の輪", "image": "10_wheel_of_fortune.jpg", "upright": "変化、循環、タイミング、抗えない流れ、偶然に見える必然", "reversed": "流れに乗れない感覚、変化への抵抗、同じ場所を回っているような感じ"},
    {"number": 11, "name_en": "JUSTICE", "name_ja": "正義", "image": "11_justice.jpg", "upright": "公平さ、判断、均衡、責任、感情に流されない視線、張り詰めた誠実さ", "reversed": "不公平感、自分への厳しさ、判断を先延ばしにすること、感情と理屈のずれ"},
    {"number": 12, "name_en": "THE HANGED MAN", "name_ja": "吊るされた男", "image": "12_hanged_man.jpg", "upright": "停止、視点の反転、信念に基づく静止、手放し、意味の熟成", "reversed": "止まっていることへの焦り、犠牲感、視点を変えられない苦しさ"},
    {"number": 13, "name_en": "DEATH", "name_ja": "死神", "image": "13_death.jpg", "upright": "終わり、変容、脱皮、避けられない区切り、新しい状態への移行", "reversed": "終わらせられなさ、変化への抵抗、過去にしがみつくこと、区切りの先延ばし"},
    {"number": 14, "name_en": "TEMPERANCE", "name_ja": "節制", "image": "14_temperance.jpg", "upright": "調和、混ざり合うもの、回復、バランス、少しずつ整えること", "reversed": "混ざらなさ、偏り、整える前に急ぎすぎること、心身のリズムの乱れ"},
    {"number": 15, "name_en": "THE DEVIL", "name_ja": "悪魔", "image": "15_devil.jpg", "upright": "執着、快楽、依存、湿った欲望、見たくない本音、鎖に見えるもの", "reversed": "鎖に気づき始めること、依存から離れる兆し、欲望との距離の取り直し"},
    {"number": 16, "name_en": "THE TOWER", "name_ja": "塔", "image": "16_tower.jpg", "upright": "崩壊、衝撃、壊れるべき構造、突然の気づき、偽りの安全の破壊", "reversed": "崩壊を避けようとすること、小さな違和感の蓄積、壊れる前の警告"},
    {"number": 17, "name_en": "THE STAR", "name_ja": "星", "image": "17_star.jpg", "upright": "希望、癒し、透明さ、祈り、遠くにある光、無防備な信頼", "reversed": "希望を信じきれないこと、癒しの途中、光が遠く感じられる状態"},
    {"number": 18, "name_en": "THE MOON", "name_ja": "月", "image": "18_moon.jpg", "upright": "不安、夢、幻想、無意識、曖昧さ、見えないものへの感受性", "reversed": "霧が晴れ始めること、不安の正体が見え始めること、幻想から覚める途中"},
    {"number": 19, "name_en": "THE SUN", "name_ja": "太陽", "image": "19_sun.jpg", "upright": "生命力、祝福、明るさ、無邪気さ、肯定、隠れない喜び", "reversed": "喜びを受け取れないこと、明るく振る舞う疲れ、少し曇った肯定感"},
    {"number": 20, "name_en": "JUDGEMENT", "name_ja": "審判", "image": "20_judgement.jpg", "upright": "呼び声、再生、目覚め、過去からの浮上、応答すること", "reversed": "呼び声を聞かないふりをすること、過去への未練、変わることへのためらい"},
    {"number": 21, "name_en": "THE WORLD", "name_ja": "世界", "image": "21_world.jpg", "upright": "完成、統合、循環の終わりと始まり、全体性、ひとつの物語の成就", "reversed": "未完了感、あと少しで統合されないもの、終わりきらない物語、完成へのためらい"},
]


NUMBER_SYMBOLS = {
    0: "空白、まだ始まっていない余地、名前のない可能性",
    1: "ひとつの点、意志、最初の輪郭",
    2: "揺れ、対話、分かれ道、他者の気配",
    3: "広がり、表現、遊び、外へこぼれるもの",
    4: "土台、境界、守り、安定させたい気持ち",
    5: "変化、違和感、動き出す衝動、風穴",
    6: "調和、世話、関係の温度、整えたい願い",
    7: "探求、距離、静かな集中、自分だけの道",
    8: "循環、力の扱い、継続、繰り返すテーマ",
    9: "手放し、成熟、終わりに近い内省",
    10: "区切り、次の周期、ひとつの流れの反転",
    11: "直感、緊張した感受性、細い光",
    12: "待つ時間、受け取る器、急がない知恵",
    13: "変質、脱皮、古い皮が剥がれる痛み",
    14: "調整、混ぜ合わせる力、回復の途中",
    15: "欲望、引力、離れがたいもの、熱",
    16: "ひび、目覚め、壊れかけた前提",
    17: "希望、遠くの灯り、まだ消えていない願い",
    18: "夢、曖昧さ、夜の感情、言葉になる前の不安",
    19: "生命力、明るさ、外へ開く力",
    20: "呼びかけ、応答、眠っていたものが起きる気配",
    21: "統合、ひとつの円、今いる場所を受け取ること",
}


def get_api_key():
    if OPENAI_API_KEY.strip():
        return OPENAI_API_KEY.strip()
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
        if secret_key:
            return secret_key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "").strip()


def get_card_meaning(card, orientation):
    return card["upright"] if orientation == "正位置" else card["reversed"]


def generate_reflection(question, chosen_number, card, impression, orientation):
    api_key = get_api_key()
    if not api_key:
        return "APIキーが設定されていません。\n\nStreamlit Cloud の Secrets に OPENAI_API_KEY を登録してください。"

    client = OpenAI(api_key=api_key)
    meaning = get_card_meaning(card, orientation)
    number_symbol = NUMBER_SYMBOLS.get(chosen_number, "問いの入口、揺らぎ")

    prompt = f"""
あなたは、未来を断定する占い師ではありません。
タロットカードを使って、ユーザーの無意識・感情・思考の癖をそっと照らし、質問者の自律と自己決定を促す内省の案内人です。

この占いは、質問者を甘やかすためのものではありません。
ただし、毎回強く諭したり、重く分析したりする必要もありません。
相談内容の重さに合わせて、文章の深度・厳しさ・助言の強さを調整してください。

軽い相談や日常的な迷いの場合は、現実逃避・責任回避・隠れた感情などを大げさに扱わず、カードの象徴を使って静かに視点を増やしてください。
重い悩み、繰り返している苦しさ、依存や不安が強く見える相談の場合だけ、より深い内省や行動への責任を促してください。

ただし、人格否定や自尊心を傷つける言い方はしないでください。
厳しさは、質問者の人生をよくするための思いやりとして使ってください。

ユーザーが選ぶ0から21の数字はカード番号そのものではありません。
数字は、質問者が問いの前で無意識に選んだ入口、水面に落とした小石、流れに触れる指先のようなものとして扱ってください。
出たカードの意味を決めるものではなく、文章全体に一文だけ自然に織り込んでください。

選んだ数字のゆるやかな象徴:
{chosen_number}: {number_symbol}

【ユーザーの悩み・問い】
{question}

【ユーザーが選んだ数字】
{chosen_number}

【ランダムに出たカード】
{card["number"]}: {card["name_en"]} / {card["name_ja"]}

【カードの向き】
{orientation}

【カードの象徴】
{meaning}

【ユーザーがカードを見て感じたこと】
{impression}

文章の方針:
- 未来を断定しない
- 相手の気持ちを決めつけない
- カードの意味を押しつけない
- ユーザーがカードを見て感じた印象を、内側の感覚を読む手がかりとして扱う
- 選んだ数字のニュアンスを、占い結果の中に一文だけ自然に織り込む
- 数字の意味を辞書のように説明しない
- 数字とカードを無理に一致させない
- 「試し行動」という言葉は原則使わない
- 「現実逃避」「責任回避」「深層心理」「隠れた感情」などの強い言葉は、相談内容が重い場合にだけ控えめに使う
- 軽い相談には軽やかに、重い相談には深く、相談の温度に合わせる
- 具体的すぎる行動指示に寄りすぎない
- このタロットは水をテーマにしているため、比喩は水に関するものを中心にする
- 水面、波紋、渦、大河、母なる海、濁流、潮の流れ、潮の満ち引き、清流、深い水底、岸辺、源流、雨、霧などを自然に使う
- 比喩を詰め込みすぎず、意味が伝わる文にする
- 感情に気づくことと、感情に飲まれて周囲にぶつけることは違う、というニュアンスを必要に応じて含める
- 社会性、思いやり、他者への敬意を失わない方向へ静かに戻す
- 不安や怒りや悲しみは否定しないが、それを理由に人間関係を壊す行動を美化しない
- どうにもならない潮の流れと、自分で舵を取れる場所を分ける
- 辛口にする場合も、人格否定ではなく、静かな目覚ましのように書く
- 文章は450から750字程度
- 最後は、質問者が自分に問い直せる一文、または小さな視点の転換で終える

文体:
- タロット占いらしい雰囲気を持たせる
- 断定ではなく「かもしれません」「のようにも見えます」を使う
- 水に関する比喩を中心に、静かで内省的な文体にする
- やさしいが、必要なところでは曖昧に逃げない
"""

    try:
        response = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return response.output_text
    except Exception as e:
        return f"AI生成中にエラーが出ました。\n\nエラー内容: {e}"


def show_card_image(image_path, orientation):
    if not image_path.exists():
        st.error(
            f"画像が見つかりません: {image_path}\n\n"
            "GitHubに cards_tiny フォルダと画像22枚がアップロードされているか確認してください。"
        )
        return
    image = Image.open(image_path)
    if orientation == "逆位置":
        image = image.rotate(180, expand=True)
    st.image(image, use_container_width=True)


def show_shuffle_animation():
    st.markdown(
        """
        <style>
        .shuffle-wrap {
            height: 230px;
            position: relative;
            margin: 22px auto 30px auto;
            max-width: 420px;
        }

        .shuffle-card {
            width: 112px;
            height: 176px;
            border-radius: 10px;
            position: absolute;
            left: 50%;
            top: 20px;
            transform: translateX(-50%);
            background:
                radial-gradient(circle at center, rgba(255, 248, 220, 0.96) 0%, rgba(230, 206, 150, 0.86) 22%, transparent 23%),
                radial-gradient(circle at center, transparent 0%, transparent 38%, rgba(95, 70, 35, 0.35) 39%, transparent 42%),
                linear-gradient(135deg, #efe0b8, #b88d42 48%, #f7edd1);
            border: 2px solid rgba(105, 72, 25, 0.78);
            box-shadow: 0 14px 34px rgba(80, 55, 25, 0.28);
            overflow: hidden;
        }

        .shuffle-card::before {
            content: "";
            position: absolute;
            inset: 10px;
            border: 1px solid rgba(255, 252, 230, 0.72);
            border-radius: 7px;
            box-shadow: inset 0 0 0 1px rgba(101, 70, 26, 0.3);
        }

        .shuffle-card::after {
            content: "*";
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -52%);
            font-size: 2.4rem;
            color: rgba(88, 61, 25, 0.72);
            text-shadow: 0 1px 0 rgba(255, 250, 225, 0.8);
        }

        .card-a { animation: shuffleA 1.35s ease-in-out infinite; }
        .card-b { animation: shuffleB 1.35s ease-in-out infinite; }
        .card-c { animation: shuffleC 1.35s ease-in-out infinite; }

        @keyframes shuffleA {
            0% { transform: translateX(-50%) rotate(0deg); }
            30% { transform: translateX(-160%) rotate(-13deg); }
            70% { transform: translateX(58%) rotate(9deg); }
            100% { transform: translateX(-50%) rotate(0deg); }
        }

        @keyframes shuffleB {
            0% { transform: translateX(-50%) rotate(0deg); }
            30% { transform: translateX(70%) rotate(12deg); }
            70% { transform: translateX(-115%) rotate(-9deg); }
            100% { transform: translateX(-50%) rotate(0deg); }
        }

        @keyframes shuffleC {
            0% { transform: translateX(-50%) rotate(0deg); }
            40% { transform: translateX(-18%) translateY(-12px) rotate(5deg); }
            80% { transform: translateX(25%) translateY(8px) rotate(-6deg); }
            100% { transform: translateX(-50%) rotate(0deg); }
        }

        .shuffle-text {
            text-align: center;
            color: #7a5b25;
            letter-spacing: 0.12em;
            margin-top: -8px;
            font-size: 0.95rem;
            font-family: Georgia, "Times New Roman", serif;
        }
        </style>

        <div class="shuffle-wrap">
            <div class="shuffle-card card-a"></div>
            <div class="shuffle-card card-b"></div>
            <div class="shuffle-card card-c"></div>
        </div>
        <div class="shuffle-text">The cards are shifting...</div>
        """,
        unsafe_allow_html=True,
    )


def reset_reading():
    st.session_state.step = 1
    st.session_state.question = ""
    st.session_state.chosen_number = 0
    st.session_state.selected_card_index = 0
    st.session_state.orientation = "正位置"
    st.session_state.impression = ""
    st.session_state.reflection = ""


for key, value in {
    "step": 1,
    "question": "",
    "chosen_number": 0,
    "selected_card_index": 0,
    "orientation": "正位置",
    "impression": "",
    "reflection": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top, rgba(255, 248, 226, 0.95), rgba(246, 239, 222, 0.96) 38%, #efe4d1 100%);
    }

    .block-container {
        max-width: 780px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    h1 {
        text-align: center;
        color: #4b3d2a;
        letter-spacing: 0.14em;
        font-family: Georgia, "Times New Roman", serif;
        font-weight: 500;
    }

    h2, h3 {
        color: #4f4638;
        letter-spacing: 0.04em;
    }

    p, label, div {
        color: #4f4638;
    }

    .intro-box,
    .question-box,
    .meaning-box,
    .reflection-box {
        background:
            linear-gradient(180deg, rgba(255, 252, 244, 0.94), rgba(246, 235, 213, 0.88));
        border: 1px solid rgba(168, 130, 62, 0.38);
        box-shadow: 0 10px 28px rgba(90, 65, 30, 0.08);
    }

    .intro-box {
        padding: 1.2rem 1.4rem;
        border-radius: 16px;
        line-height: 1.9;
        margin-bottom: 1.5rem;
    }

    .question-box,
    .meaning-box {
        padding: 1rem 1.2rem;
        border-radius: 14px;
        line-height: 1.8;
        margin-bottom: 1.2rem;
    }

    .card-title {
        text-align: center;
        font-size: 1.55rem;
        letter-spacing: 0.16em;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
        color: #7a5b25;
        font-family: Georgia, "Times New Roman", serif;
    }

    .card-subtitle {
        text-align: center;
        font-size: 1rem;
        margin-bottom: 0.6rem;
        color: #6d6355;
    }

    .orientation {
        text-align: center;
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 999px;
        background: rgba(184, 155, 94, 0.18);
        border: 1px solid rgba(155, 112, 42, 0.48);
        color: #705426;
        margin: 0 auto 1.2rem auto;
        letter-spacing: 0.08em;
    }

    .center {
        text-align: center;
    }

    .reflection-box {
        padding: 1.4rem 1.5rem;
        border-left: 4px solid #b89b5e;
        border-radius: 12px;
        line-height: 2;
        white-space: pre-wrap;
    }

    .small-note {
        font-size: 0.9rem;
        color: #7d715f;
        line-height: 1.8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.title("Tarot Reflection")

st.markdown(
    """
    <div class="intro-box">
    これは未来を断定する占いではありません。<br>
    タロットカードの象徴と、あなた自身が絵から受け取った印象を通して、<br>
    まだ言葉になっていない感覚をそっと見つけるための場所です。
    </div>
    """,
    unsafe_allow_html=True,
)


if st.session_state.step == 1:
    st.subheader("1. 問いを置く")

    question = st.text_area(
        "いま考えたい悩みや問いを書いてください。",
        placeholder="例：この関係を続けるべきか迷っている / 今の仕事に違和感がある / 自分が本当は何を望んでいるのか知りたい",
        height=140,
        value=st.session_state.question,
    )

    chosen_number = st.slider(
        "0から21の中から、いま気になる数字をひとつ選んでください。",
        min_value=0,
        max_value=21,
        value=st.session_state.chosen_number,
        step=1,
    )

    st.markdown(
        """
        <div class="small-note">
        ※ 選んだ数字はカード番号ではありません。<br>
        カードを開く前の、小さな儀式として扱われます。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("カードをひらく", use_container_width=True):
        if not question.strip():
            st.warning("まず、悩みや問いを書いてください。")
        else:
            st.session_state.question = question.strip()
            st.session_state.chosen_number = chosen_number
            st.session_state.selected_card_index = random.randint(0, 21)
            st.session_state.orientation = random.choice(["正位置", "逆位置"])

            show_shuffle_animation()
            time.sleep(1.6)

            st.session_state.step = 2
            st.rerun()


elif st.session_state.step == 2:
    card = TAROT_CARDS[st.session_state.selected_card_index]
    orientation = st.session_state.orientation
    image_path = CARDS_DIR / card["image"]
    meaning = get_card_meaning(card, orientation)

    st.subheader("2. カードを見る")

    st.markdown("#### あなたの問い")
    st.markdown(
        f"""
        <div class="question-box">
        {st.session_state.question}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card-title">{card["name_en"]}</div>
        <div class="card-subtitle">{card["number"]} / {card["name_ja"]}</div>
        <div class="center"><span class="orientation">{orientation}</span></div>
        """,
        unsafe_allow_html=True,
    )

    show_card_image(image_path, orientation)

    st.markdown(
        f"""
        <div class="meaning-box">
        <strong>このカードのひとつの象徴：</strong><br>
        {meaning}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### このカードを見て、何を感じましたか？")

    impression = st.text_area(
        "正解っぽく書かなくて大丈夫です。目に入ったもの、怖い/安心する/引っかかる感じ、色や人物への印象などを自由に書いてください。",
        placeholder="例：明るいけど少し怖い。人物が前を向いている感じがして、自分も進みたいのかもしれないと思った。",
        height=150,
        value=st.session_state.impression,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("戻る", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    with col2:
        if st.button("内省文を生成する", use_container_width=True):
            if not impression.strip():
                st.warning("カードを見て感じたことを書いてください。")
            else:
                st.session_state.impression = impression.strip()

                with st.spinner("言葉になりきらない感覚を、そっと拾っています..."):
                    st.session_state.reflection = generate_reflection(
                        question=st.session_state.question,
                        chosen_number=st.session_state.chosen_number,
                        card=card,
                        impression=st.session_state.impression,
                        orientation=orientation,
                    )

                st.session_state.step = 3
                st.rerun()


elif st.session_state.step == 3:
    card = TAROT_CARDS[st.session_state.selected_card_index]
    orientation = st.session_state.orientation
    image_path = CARDS_DIR / card["image"]

    st.subheader("3. 内省のための言葉")

    st.markdown(
        f"""
        <div class="card-title">{card["name_en"]}</div>
        <div class="card-subtitle">{card["number"]} / {card["name_ja"]}</div>
        <div class="center"><span class="orientation">{orientation}</span></div>
        """,
        unsafe_allow_html=True,
    )

    show_card_image(image_path, orientation)

    st.markdown("#### あなたの問い")
    st.write(st.session_state.question)

    st.markdown("#### あなたが選んだ数字")
    st.write(st.session_state.chosen_number)

    st.markdown("#### カードを見て感じたこと")
    st.write(st.session_state.impression)

    st.markdown("#### 内省文")
    st.markdown(
        f"""
        <div class="reflection-box">
        {st.session_state.reflection}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("もう一度ひく", use_container_width=True):
        reset_reading()
        st.rerun()
