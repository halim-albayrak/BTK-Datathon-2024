import pandas as pd
import numpy as np


def renamer(data):

    renamer_dict = {}
    for col in data.columns:
        new_col = col.lower()
        new_col = (
            new_col.replace(" ", "_")
            .replace("ö", "o")
            .replace("ü", "u")
            .replace("?", "")
        )
        renamer_dict[col] = new_col

    data.rename(columns=renamer_dict, inplace=True)

    return data


def string_fixer(x):
    return (
        x.replace("â", "a")
        .replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("i̇", "i")
        .replace("ö", "o")
        .replace("ü", "u")
        .replace("ş", "s")
    )


def date_formatter(dt):

    year = 18
    month = dt

    if pd.isna(dt):

        return year, month

    len_dt = len(dt)

    dt = string_fixer(dt.lower())

    months_tr = [
        "ocak",
        "subat",
        "mart",
        "nisan",
        "mayis",
        "haziran",
        "temmuz",
        "agustos",
        "eylul",
        "ekim",
        "kasim",
        "aralik",
    ]

    for i in range(12):

        if months_tr[i] in dt:

            year = dt.split(" ")[1]
            month = i + 1
            return year, month

    months_eng = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]

    for i in range(12):

        if months_eng[i] in dt:

            year = dt.split("-")[1]
            month = i + 1
            return year, month

    if len_dt == 19:

        year = dt.split("-")[0]
        month = dt.split("-")[1]

    elif len_dt in [15, 16]:

        year = dt.split(" ")[0].split(".")[2]
        month = dt.split(".")[1]

    elif len_dt in [14]:

        year = dt.split(" ")[2]
        month = 12

    elif len_dt in [11, 12, 13]:

        year = dt.split(" ")[0].split("/")[2]
        month = dt.split("/")[0]

    elif len_dt in [10, 9, 8]:

        if "-" in dt:

            year = dt.split("-")[0]
            month = dt.split("-")[1]

        else:

            year = dt.split("/")[2]
            month = dt.split("/")[1]

    return year, month


def year_fixer(x):

    x = str(x)

    if "_" in x:

        x = x.replace("_", "")

    if x.isnumeric():

        if len(x) == 2:

            if int(x) < 18:

                return int("20" + x)

            return int("19" + x)

        elif len(x) == 3:

            if int(x) < 100:

                return int("2" + x)

            return int("1" + x)

        if int(x) < 1980:

            return 18

        return int(x)

    return 18


def month_fixer(x):
    x = str(x)
    if x.isnumeric():

        if int(x) <= 12 and int(x) >= 1:

            return int(x)

        else:

            return np.nan

    return np.nan


def dogum_yil_fixer(basvuru, uni_sinif):

    if uni_sinif == "hazirlik":

        uni_sinif = 0

    else:

        uni_sinif = int(uni_sinif)

    dogum_yil = basvuru - 18 - uni_sinif

    return dogum_yil


def preprocesser(df, train_process=True):

    drop_cols = [
        "dogum_yeri",
        "dogum_tarihi",
        "dogum_yil_ay",
        "ikametgah_sehri",
        "lise_adi",
        "lise_bolum_diger",
        "uye_oldugunuz_kulubun_ismi",
        "hangi_stk'nin_uyesisiniz",
        "stk_projesine_katildiniz_mi",
        "girisimcilikle_ilgili_deneyiminizi_aciklayabilir_misiniz",
        "ingilizce_seviyeniz",
        "daha_onceden_mezun_olunduysa,_mezun_olunan_universite",
        "burslu_ise_burs_yuzdesi",
        "lise_adi_diger",
        "daha_once_baska_bir_universiteden_mezun_olmus",
        "lise_sehir",
        "baska_kurumdan_aldigi_burs_miktari",
    ]

    # cinsiyet
    df["cinsiyet"].fillna("Belirtmek istemiyorum", inplace=True)
    df["cinsiyet"] = df["cinsiyet"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )

    # dogum_yili
    df["dogum_yil_ay"] = df["dogum_tarihi"].apply(lambda x: date_formatter(x))
    df["dogum_yil"] = df["dogum_yil_ay"].apply(lambda x: x[0])
    df["dogum_ay"] = df["dogum_yil_ay"].apply(lambda x: x[1])
    df["dogum_yil"] = df["dogum_yil"].apply(
        lambda x: 0 if pd.isna(x) else year_fixer(x)
    )
    df.loc[(df["dogum_yil"] <= 1970) | (df["dogum_yil"] >= 2007), "dogum_yil"] = np.nan
    df["dogum_ay"] = df["dogum_ay"].apply(lambda x: x if pd.isna(x) else month_fixer(x))

    if train_process:

        dogum_mapping = pd.read_csv("data/dogum_yerleri_coordinate_mapping_train.csv")
        ikamethag_mapping = pd.read_csv(
            "data/ikametgah_yerleri_coordinate_mapping_train.csv"
        )
        lise_mapping = pd.read_csv("data/lise_yerleri_coordinate_mapping_train.csv")

    else:

        dogum_mapping = pd.read_csv("data/dogum_yerleri_coordinate_mapping_test.csv")
        ikamethag_mapping = pd.read_csv(
            "data/ikametgah_yerleri_coordinate_mapping_test.csv"
        )
        lise_mapping = pd.read_csv("data/lise_yerleri_coordinate_mapping_test.csv")

    # dogum_yeri
    df = df.merge(
        dogum_mapping[["location", "lat", "lon"]],
        left_on="dogum_yeri",
        right_on="location",
        how="left",
    )
    df.drop("location", axis=1, inplace=True)
    df.rename(columns={"lat": "lat_dogum", "lon": "lon_dogum"}, inplace=True)

    # ikametgah_sehri
    df = df.merge(
        ikamethag_mapping[["location", "lat", "lon"]],
        left_on="ikametgah_sehri",
        right_on="location",
        how="left",
    )
    df.drop("location", axis=1, inplace=True)
    df.rename(columns={"lat": "lat_ikametgah", "lon": "lon_ikametgah"}, inplace=True)

    # universite_adi
    df["universite_adi"] = df["universite_adi"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )

    # universite_turu
    df["universite_turu"] = df["universite_turu"].apply(
        lambda x: x if pd.isna(x) else x.lower()
    )
    df["universite_turu"].fillna("devlet", inplace=True)

    # burs_aliyor_mu
    df["burs_aliyor_mu"] = df["burs_aliyor_mu"].apply(
        lambda x: x if pd.isna(x) else x.lower()
    )

    # bolum
    df["bolum"] = df["bolum"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df["bolum"] = df["bolum"].apply(
        lambda x: x if pd.isna(x) else x.split("(")[0].split("/")[0]
    )

    # universite_kacinci_sinif
    df["universite_kacinci_sinif"] = df["universite_kacinci_sinif"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[df["universite_kacinci_sinif"] == "0", "universite_kacinci_sinif"] = (
        "hazirlik"
    )
    df.loc[df["universite_kacinci_sinif"] == "tez", "universite_kacinci_sinif"] = (
        "yuksek lisans"
    )
    df.loc[df["universite_kacinci_sinif"] == "5", "universite_kacinci_sinif"] = "4"
    df.loc[df["universite_kacinci_sinif"] == "6", "universite_kacinci_sinif"] = "4"

    # universite_not_ortalamasi
    lower_group = [
        "2.50 ve altı",
        "2.00 - 2.50",
        "1.80 - 2.49",
        "1.00 - 2.50",
        "0 - 1.79",
    ]
    df.loc[
        df["universite_not_ortalamasi"].isin(lower_group), "universite_not_ortalamasi"
    ] = "2.50 - 0.00"
    lower_mid_group = [
        "3.00-2.50",
        "2.50 - 3.00",
        "2.50 - 2.99",
        "2.50 -3.00",
        "0 - 1.79",
    ]
    df.loc[
        df["universite_not_ortalamasi"].isin(lower_mid_group),
        "universite_not_ortalamasi",
    ] = "3.00 - 2.50"
    mid_group = ["3.00 - 3.49", "3.00 - 3.50", "3.50-3", "3.00 - 4.00"]
    df.loc[
        df["universite_not_ortalamasi"].isin(mid_group), "universite_not_ortalamasi"
    ] = "3.50 - 3.00"
    upper_group = ["3.50 - 4.00", "4.0-3.5", "4-3.5"]
    df.loc[
        df["universite_not_ortalamasi"].isin(upper_group), "universite_not_ortalamasi"
    ] = "4.00 - 3.50"
    hazirlik_group = [
        "ORTALAMA BULUNMUYOR",
        "Hazırlığım",
        "Ortalama bulunmuyor",
        "Not ortalaması yok",
    ]
    df.loc[
        df["universite_not_ortalamasi"].isin(hazirlik_group),
        "universite_not_ortalamasi",
    ] = "ortalama_yok"

    df.loc[
        (df["universite_not_ortalamasi"].isnull())
        & (df["universite_kacinci_sinif"] == "hazirlik"),
        "universite_not_ortalamasi",
    ] = "ortalama_yok"

    df.loc[
        (df["universite_not_ortalamasi"].isnull())
        & (df["universite_kacinci_sinif"] != "hazirlik"),
        "universite_not_ortalamasi",
    ] = "3.00 - 2.50"

    # lise_turu
    df["lise_turu"] = df["lise_turu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )

    df.loc[
        df["lise_turu"].isin(
            [
                "anadolu lisesi",
                "diger",
                "duz lise",
                "devlet",
                "meslek lisesi",
                "fen lisesi",
                "meslek",
                "imam hatip lisesi",
            ]
        ),
        "lise_turu",
    ] = "devlet"
    df.loc[df["lise_turu"].isin(["ozel", "ozel lisesi", "ozel lise"]), "lise_turu"] = (
        "ozel"
    )
    df["lise_turu"].fillna("devlet", inplace=True)

    # lise_bolumu
    df["lise_bolumu"] = df["lise_bolumu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df["lise_bolumu"].fillna("sayisal", inplace=True)

    esit_agirlik_values = ["tm", "esit", "ea", "turkce", "agirlik"]
    for val in esit_agirlik_values:
        df.loc[df["lise_bolumu"].str.contains(val), "lise_bolumu"] = "esit agirlik"
    sayisal_values = ["fen", "mf", "fm", "sayisal"]
    for val in sayisal_values:
        df.loc[df["lise_bolumu"].str.contains(val), "lise_bolumu"] = "sayisal"
    sozel_values = ["sozel", "ts"]
    for val in sozel_values:
        df.loc[df["lise_bolumu"].str.contains(val), "lise_bolumu"] = "sozel"
    dil_values = ["dil", "yabanci", "ingilizce", "ydl"]
    for val in dil_values:
        df.loc[df["lise_bolumu"].str.contains(val), "lise_bolumu"] = "dil"

    df.loc[
        df["lise_bolumu"].isin(["sayisal", "esit agirlik", "sozel", "dil"]) == False,
        "lise_bolumu",
    ] = "sayisal"

    # lise_sehir
    df["lise_sehir"] = df["lise_sehir"].apply(lambda x: x if pd.isna(x) else x.lower())
    df = df.merge(
        lise_mapping[["location", "lat", "lon"]],
        left_on="lise_sehir",
        right_on="location",
        how="left",
    )
    df.drop("location", axis=1, inplace=True)
    df.rename(columns={"lat": "lat_lise", "lon": "lon_lise"}, inplace=True)

    # lise_mezuniyet_notu
    upper_group = [
        "75 - 100",
        "84-70",
        "100-85",
        "4.00-3.50",
        "3.00 - 4.00",
        "3.50-3.00",
        "3.50-3",
    ]
    df.loc[
        df["lise_mezuniyet_notu"].isin(upper_group),
        "lise_mezuniyet_notu",
    ] = "75 - 100"
    mid_group = [
        "50 - 75",
        "69-55",
        "3.00-2.50",
        "50 - 74",
        "2.50 ve altı",
        "54-45",
        "Not ortalaması yok",
    ]
    df.loc[df["lise_mezuniyet_notu"].isin(mid_group), "lise_mezuniyet_notu"] = "50 - 74"
    lower_group = ["25 - 50", "44-0", "0 - 25", "25 - 49" "0 - 24"]
    df.loc[df["lise_mezuniyet_notu"].isin(lower_group), "lise_mezuniyet_notu"] = (
        "25 - 49"
    )
    df.loc[df["lise_mezuniyet_notu"] == "0 - 24", "lise_mezuniyet_notu"] = "25 - 49"
    df["lise_mezuniyet_notu"].fillna("50 - 74", inplace=True)

    # baska_bir_kurumdan_burs_aliyor_mu
    df["baska_bir_kurumdan_burs_aliyor_mu"] = df[
        "baska_bir_kurumdan_burs_aliyor_mu"
    ].apply(lambda x: x if pd.isna(x) else string_fixer(x.lower()))
    df["baska_bir_kurumdan_burs_aliyor_mu"].fillna("hayir", inplace=True)

    # burs_aldigi_baska_kurum
    df["burs_aldigi_baska_kurum"] = df["burs_aldigi_baska_kurum"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df["burs_aldigi_baska_kurum"].fillna("yok", inplace=True)
    kyk_values = ["kyk", "kredi", "yurtlar", "devlet"]
    for val in kyk_values:
        df.loc[
            df["burs_aldigi_baska_kurum"].str.contains(val), "burs_aldigi_baska_kurum"
        ] = "kyk"
    df.loc[
        df["burs_aldigi_baska_kurum"] == "-",
        "burs_aldigi_baska_kurum",
    ] = "yok"
    df.loc[
        df["burs_aldigi_baska_kurum"].isin(["yok", "kyk"]) == False,
        "burs_aldigi_baska_kurum",
    ] = "diger"

    # anne_egitim_durumu
    df["anne_egitim_durumu"] = df["anne_egitim_durumu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[
        df["anne_egitim_durumu"].isin(["egitim yok", "egitimi yok"]),
        "anne_egitim_durumu",
    ] = "egitim_yok"
    df.loc[
        df["anne_egitim_durumu"].isin(["ilkokul mezunu", "ilkokul"]),
        "anne_egitim_durumu",
    ] = "ilkokul"
    df.loc[
        df["anne_egitim_durumu"].isin(["ortaokul mezunu", "ortaokul"]),
        "anne_egitim_durumu",
    ] = "ortaokul"
    df.loc[
        df["anne_egitim_durumu"].isin(["lise", "lise mezunu"]), "anne_egitim_durumu"
    ] = "lise"
    df.loc[
        df["anne_egitim_durumu"].isin(["universite mezunu", "universite"]),
        "anne_egitim_durumu",
    ] = "universite"
    df.loc[
        df["anne_egitim_durumu"].isin(
            [
                "yuksek lisans",
                "doktora",
                "yuksek lisans / doktora",
                "yuksek lisans / doktara",
            ]
        ),
        "anne_egitim_durumu",
    ] = "yuksek_egitim"
    df["anne_egitim_durumu"].fillna("bilinmiyor", inplace=True)
    df.loc[
        df["anne_egitim_durumu"] == "bilinmiyor",
        "anne_egitim_durumu",
    ] = "ilkokul"

    # anne_calisma_durumu
    df["anne_calisma_durumu"] = df["anne_calisma_durumu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[df["anne_calisma_durumu"].isin(["emekli"]), "anne_calisma_durumu"] = "evet"
    df["anne_calisma_durumu"].fillna("hayir", inplace=True)

    # anne_sektor
    df["anne_sektor"] = df["anne_sektor"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[df["anne_sektor"].isin(["0", "-"]), "anne_sektor"] = "calismiyor"
    df["anne_sektor"].fillna("calismiyor", inplace=True)

    # baba_egitim_durumu
    df["baba_egitim_durumu"] = df["baba_egitim_durumu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[
        df["baba_egitim_durumu"].isin(["egitim yok", "egitimi yok"]),
        "baba_egitim_durumu",
    ] = "egitim_yok"
    df.loc[
        df["baba_egitim_durumu"].isin(["ilkokul mezunu", "ilkokul"]),
        "baba_egitim_durumu",
    ] = "ilkokul"
    df.loc[
        df["baba_egitim_durumu"].isin(["ortaokul mezunu", "ortaokul"]),
        "baba_egitim_durumu",
    ] = "ortaokul"
    df.loc[
        df["baba_egitim_durumu"].isin(["lise", "lise mezunu"]), "baba_egitim_durumu"
    ] = "lise"
    df.loc[
        df["baba_egitim_durumu"].isin(["universite mezunu", "universite"]),
        "baba_egitim_durumu",
    ] = "universite"
    df.loc[
        df["baba_egitim_durumu"].isin(
            [
                "yuksek lisans",
                "doktora",
                "yuksek lisans / doktora",
                "yuksek lisans / doktara",
            ]
        ),
        "baba_egitim_durumu",
    ] = "yuksek_egitim"
    df["baba_egitim_durumu"].fillna("bilinmiyor", inplace=True)
    df.loc[df["baba_egitim_durumu"] == "0", "baba_egitim_durumu"] = "bilinmiyor"
    df.loc[
        df["baba_egitim_durumu"] == "bilinmiyor",
        "baba_egitim_durumu",
    ] = "ilkokul"

    # baba_calisma_durumu
    df["baba_calisma_durumu"] = df["baba_calisma_durumu"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[df["baba_calisma_durumu"].isin(["emekli"]), "baba_calisma_durumu"] = "evet"
    df["baba_calisma_durumu"].fillna("hayir", inplace=True)

    # baba_sektor
    df["baba_sektor"] = df["baba_sektor"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[df["baba_sektor"].isin(["0", "-"]), "baba_sektor"] = "calismiyor"
    df["baba_sektor"].fillna("calismiyor", inplace=True)

    # kardes_sayisi
    if train_process:
        df.loc[
            df["kardes_sayisi"] == "Kardeş Sayısı 1 Ek Bilgi Aile Hk. Anne Vefat",
            "kardes_sayisi",
        ] = 1
        df["kardes_sayisi"] = df["kardes_sayisi"].apply(
            lambda x: 0 if pd.isna(x) else int(x)
        )
    df.loc[df["kardes_sayisi"] >= 4, "kardes_sayisi"] = 4

    # girisimcilik_kulupleri_tarzi_bir_kulube_uye_misiniz
    df["girisimcilik_kulupleri_tarzi_bir_kulube_uye_misiniz"] = df[
        "girisimcilik_kulupleri_tarzi_bir_kulube_uye_misiniz"
    ].apply(lambda x: x if pd.isna(x) else string_fixer(x.lower()))
    df["girisimcilik_kulupleri_tarzi_bir_kulube_uye_misiniz"].fillna(
        "hayir", inplace=True
    )

    # profesyonel_bir_spor_daliyla_mesgul_musunuz
    df["profesyonel_bir_spor_daliyla_mesgul_musunuz"] = df[
        "profesyonel_bir_spor_daliyla_mesgul_musunuz"
    ].apply(lambda x: x if pd.isna(x) else string_fixer(x.lower()))
    df["profesyonel_bir_spor_daliyla_mesgul_musunuz"].fillna("hayir", inplace=True)

    # spor_dalindaki_rolunuz_nedir
    df["spor_dalindaki_rolunuz_nedir"] = df["spor_dalindaki_rolunuz_nedir"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df.loc[
        df["spor_dalindaki_rolunuz_nedir"].isin(["0", "-"]),
        "spor_dalindaki_rolunuz_nedir",
    ] = "yok"
    df.loc[
        df["spor_dalindaki_rolunuz_nedir"].isin(["bireysel spor", "bireysel"]),
        "spor_dalindaki_rolunuz_nedir",
    ] = "biyersel spor"
    df.loc[
        df["spor_dalindaki_rolunuz_nedir"].isin(
            ["lider/kaptan", "kaptan", "kaptan / lider"]
        ),
        "spor_dalindaki_rolunuz_nedir",
    ] = "lider"
    df["spor_dalindaki_rolunuz_nedir"].fillna("yok", inplace=True)

    # aktif_olarak_bir_stk_uyesi_misiniz
    df["aktif_olarak_bir_stk_uyesi_misiniz"] = df[
        "aktif_olarak_bir_stk_uyesi_misiniz"
    ].apply(lambda x: x if pd.isna(x) else string_fixer(x.lower()))
    df["aktif_olarak_bir_stk_uyesi_misiniz"].fillna("hayir", inplace=True)

    # girisimcilikle_ilgili_deneyiminiz_var_mi
    df["girisimcilikle_ilgili_deneyiminiz_var_mi"] = df[
        "girisimcilikle_ilgili_deneyiminiz_var_mi"
    ].apply(lambda x: x if pd.isna(x) else string_fixer(x.lower()))
    df["girisimcilikle_ilgili_deneyiminiz_var_mi"].fillna("hayir", inplace=True)

    # ingilizce_biliyor_musunuz
    df["ingilizce_biliyor_musunuz"] = df["ingilizce_biliyor_musunuz"].apply(
        lambda x: x if pd.isna(x) else string_fixer(x.lower())
    )
    df["ingilizce_biliyor_musunuz"].fillna("hayir", inplace=True)

    df.drop(columns=drop_cols, inplace=True)

    ## AFTER EDA CHANGES

    df.drop(
        df.loc[
            (df["universite_kacinci_sinif"].isin(["mezun", "yuksek lisans"]))
            | (df["universite_kacinci_sinif"].isnull()),
            :,
        ].index,
        axis=0,
        inplace=True,
    )

    df.reset_index(inplace=True, drop=True)

    df.loc[df["dogum_yil"].isnull(), "dogum_yil"] = df.loc[
        df["dogum_yil"].isnull(), ["basvuru_yili", "universite_kacinci_sinif"]
    ].apply(
        lambda x: dogum_yil_fixer(x.basvuru_yili, x.universite_kacinci_sinif), axis=1
    )

    df["yas"] = df["basvuru_yili"] - df["dogum_yil"]

    return df


def main_reader(type):

    if type == "train":

        df = pd.read_csv("data/train.csv")
        df = renamer(df)
        df = preprocesser(df)
        return df

    elif type == "test":

        df = pd.read_csv("data/test_x.csv")
        df = renamer(df)
        df = preprocesser(df)
        return df

    raise "Error"
