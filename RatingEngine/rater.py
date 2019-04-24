def abc(column_name, value, *args, **kwargs):
    print(str(*args))

def ocen_cene():
    wyszukaj_inne_oferty()
    porownaj_z_innymi_ofertami()
    jesli_lepsza_od_innych_wys_ocena()

functions_to_apply = {
    'offer_url': [abc]
    'price': [ocen_cene]
}
