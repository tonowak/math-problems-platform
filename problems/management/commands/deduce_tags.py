import re
from django.core.management.base import BaseCommand, CommandError

from tags.models import Tag
from problems.models import Problem

def deduce_tags(problem):
    tags = []
    solution = problem.solution.lower()
    statement = problem.statement.lower()

    def count(expr, text = solution):
        a = 0
        for e in expr:
            a = a + len(re.findall(e, text))
        return a

    def check_solve(nazwa, lista, lower_bound, wymagania = []):
        bound = lower_bound * len(solution) * 0.0004
        tag = Tag.objects.get(name=nazwa)
        if len(wymagania):
            for x in wymagania:
                if not x:
                    return False
        ret = (count(lista) >= bound)
        if ret:
            tags.append(tag)
        return ret

    def check_statement(nazwa, lista, bound, wymagania = []):
        tag = Tag.objects.get(name=nazwa)
        if len(wymagania):
            for x in wymagania:
                if not x:
                    return False
        ret = (count(lista, statement) >= bound)
        if ret:
            tags.append(tag)
        return ret

    # GEOMETRIA <3 <3 <3
    geo = (count(["[A-Z]{2}"], problem.solution) >= 4 and count(["zbi[oó]r", "liczb", "nwd"]) <= 1) # zespo póki co sobie daruję
    # print(geo)
   
    odcinki = False
    if count(["długoś", "odcine?k", "\s[A-Z]{2}\s?(\+|-|\=)"], problem.solution) >= 4:
        check_solve("długości odcinków", [], 0)
        odcinki = True

    proporcje = check_solve("proporcje odcinków", ["frac"], 6, [geo, count(["odcine?k"]) >= 2])
     
    check_solve("rachunek kątów", ["(spherical|measured|\W)angle", "\skąt"], 6, [geo])

    check_statement("rachunek pól", ["\sp[oó]l[aeuo\s]"], 1, [geo])

    współliniowość = check_statement("współliniowość", ["współliniow", "na jednej prostej"], 1, [geo])

    współpękowość = check_statement("współpękowość", ["współpękow", "w jednym punkcie"], 1, [geo])

    okręgi = check_solve("cykliczność", ["okr[ąę]g", "cykliczny"], 2, [geo])

    check_statement("konstrukcje", ["konstru", "zbud(uj|ować)"], 1, [geo])

    stereo = check_statement("stereometria", ["ścian", "kula", "sfera", "płaszczyzn", "przestrze[nń]"], 1, [geo])

    zespo = check_solve("liczby zespolone", ["zespolon"], 1)

    trygo = check_solve("trygonometria", ["\\\\sin", "\\\\tan", "\\\\tg", "\\\\cos", "\\\\cot", "\\\\ctg", "sinus", "[ck]osinus", "tangens", "[ck]otangens"], 5)

    wektor = check_solve("rachunek wektorowy", ["wektor"], 3)
     
    hardeTrygo = (count(["\\\\sin", "\\\\tan", "\\\\tg", "\\\\cos", "\\\\cot", "\\\\ctg"]) >= 20)
    if geo and (zespo or wektor or hardeTrygo):
        check_solve("geometria analityczna", [], 0)
     
    # nierówność trójkąta nie zawsze jest w geo...
    check_solve("nierówność trójkąta", ["nierównoś"], 0.4, [geo or (count(["trójkąt"], statement) >= 1 and not geo)])
     
    check_solve("twierdzenie o czapce krasnoludka", ["(najmocniejsz.{1,3}|zasadnicz.{1,3}) twierdzeni.{1,2} planimetrii", "krasnoludka", "\sstyczn"], 3, [geo, odcinki])

    check_solve("przystawanie trójkątów", ["przystając", "\\\\equiv", "\\\\cong"], 3, [geo, count("trójkąt") >= 1])

    check_solve("podobieństwa trójkątów", ["\spodob", "\\\\sim", "~"], 3, [geo, count("trójkąt") >= 1])

    check_solve("izometrie płaszczyzny", ["obr[oó][tc]", "\ssymetr", "translacj", "\sprzesu", "o wektor"], 3, [geo])

    check_solve("twierdzenie Pitagorasa", ["pitagoras"], 0.4, [geo])

    check_solve("twierdzenie o trójliściu", ["trójliś", "trójn[oó]g"], 0.4, [geo])

    check_solve("twierdzenie Talesa", ["tales"], 1, [proporcje])

    check_solve("jednokładności", ["jednokładn"], 1, [geo])

    check_solve("twierdzenie o dwusiecznej", ["dwusieczn"], 2, [proporcje])

    check_solve("twierdzenie Menelaosa", ["menela[ou]s"], 0.4, [współliniowość])

    check_solve("twierdzenie Cevy", ["cev"], 0.4, [współpękowość])

    potęga = check_solve("potęga punktu względem okręgu", ["potęg"], 0.4, [okręgi])

    check_solve("czworokąty cykliczne", ["(wpisać|opisać można)", "na jednym okręgu", "czworokąt"], 2, [okręgi])

    check_solve("inwersja względem okręgu", ["\sinwersj"], 1, [okręgi])

    check_solve("osie potęgowe", ["\so(ś|si)"], 0.4, [potęga])

    # ATL
    # mimo wszystko solve, bo czasem jest ukryty wątek podzielności
    wielomian = check_solve("wielomiany", ["wielomian", "pierwiaste?k"], 1, [count(["kwadratow"], solution) == 0])

    podzielnosc = check_solve("podzielności i kongruencje", ["podzieln", "nwd", "reszt", "dziele?ni", "\smodulo", "equiv", "wielokrotnoś"], 2, [not geo, not wielomian])

    check_solve("reszty kwadratowe", ["kwadrat", "sześcian"], 3, [podzielnosc, not geo])

    check_solve("rzędy i półrzędy", ["twierdzeni\w Fermat", "rząd"], 2, [not geo, podzielnosc])

    padic = check_solve("wykładniki p-adyczne", ["ajwiększa potęga ..? (jaka|która) dzieli", "v_[p\d]"], 3, [podzielnosc, not geo])

    check_solve("lemat o zwiększaniu wykładnika", ["lte", "emat.{1,3} o zwiększaniu wykładnika"], 0.4, [padic, not geo])

    check_solve("chińskie twierdzenie o resztach", ["chiński.{1,3} twierdzeni"], 0.4, [podzielnosc, not geo])

    check_statement("ciągi rekurencyjne", ["określony", "wyznacz[ya]", "rekurencyjn", "równani[ae]", "\w\_\{?\d\}?\s?\=\s?\d"], 3, [count(["ciąg"], statement) >= 1, not geo])

    check_solve("ciąg Fibonacciego", ["fibonacci", "f_"], 3, [not geo])

    niewym = check_statement("liczby niewymierne", ["niewymiern"], 1, [not geo])

    check_statement("liczby wymierne", ["wymiern"], 1, [not niewym, not geo])

    # równanie Diofantyczne
    diofantyczne = check_statement("równania diofantyczne", ["naturaln", "całkowit", "równani"], 2, [count(["rzeczywist", "ciąg"], solution) == 0, not geo, count(["naturaln", "całkowit"], statement) >= 1])

    check_solve("równanie Pella", ["pell", "indyjski"], 0.4, [not geo])

    check_solve("trójmiany kwadratowe", ["równa.{1,3} kwadratow", "trójmian", "funkcj. kwadratow"], 0.4, [not geo, not wielomian])

    check_solve("wzory Viete'a", ["viet"], 1, [wielomian])
     
    # KOMBI (bez serduszek)
    check_solve("zasada indukcji matematycznej", ["indukc"], 1)
     
    # check_solve("zasada minimum/maksimum", ["niech", "śród", "wybierz", "moż", "rozważ", "weź", "rozpatrz"], 2, [count(["minimaln", "maksymaln", "największ", "najmniejsz"]) >= 1, not geo])
    kombi_geo = check_statement("geometria kombinatoryczna", ["kąt", "ścian", "płaszczyzn"], 2, [not geo, not trygo, len(tags) < 2])

    check_solve("zasada minimum/maksimum", ["(niech |śród |wybierzmy |rozważ| weźmy| rozpatrz).{1,20}(minimaln|maksymaln|najmniejsz|największ)"], 0.4, [not geo])
     
    check_solve("zasada szufladkowa Dirichleta", ["szufladkow", "dirichlet"], 1)
     
    zbiory = (count(["zbi[oó]r"]) >= 3)

    graf = check_solve("grafy", ["graf", "krawęd", "wierzchoł"], 2, [not geo, not kombi_geo, not stereo])

    check_solve("drzewa", ["drzew"], 1, [graf])

    check_solve("cykle", ["cykl"], 1, [graf])

    check_solve("grafy skierowane", ["krawęd.{1, 5} (wy?chodz|od |do |prowadz|skierowan)", "skierowan"], 3, [graf])

    check_solve("twierdzenie Halla", ["hall"], 1, [graf])

    check_statement("gry", ["gra\s", "dwóch graczy", "grę\s", "zaczyna", "\sruch", "\soperacj"], 1, [not geo])

    check_solve("dwumian Newtona", ["binom", "choose"], 3)

    check_statement("permutacje", ["permutacj"], 1)

    check_solve("kolorowania", ["kolor"], 2, [count(["kolor", "czerw", "niebiesk", "zielon", "żółt"], statement) == 0])

    check_solve("niezmienniki i półniezmienniki", ["niezmienn", "półniezmienn"], 1, [len(tags) < 2])

    check_solve("zasada włączeń i wyłączeń", ["włączeń i wyłączeń"], 0.4, [zbiory])

    check_solve("podwójne zliczanie", ["na dwa sposoby", "zliczy"], 2, [len(tags) < 2])

    check_solve("prawdopodobieństwo", ["prawdopodobieństw"], 0.4)

    # wykończy mnie ta kombi
    # lepiej najpierw dopiszę ANAL
    check_statement("układy równań", ["układ.? równań", "left\\\\{\\\\begin\{array"], 1, [count(["znajdź", "znaleźć", "rozwiąż", "rozwiąza", "wyznacz", "spełniając"], statement) >= 1, not diofantyczne])
    
    check_solve("tożsamość nieśmiertelna", ["\w\^.{1,7}\s?-\s?\w\^.{1,7}\s?=\s?\(\w.{1,7}-\s?\w.{1,7}\)"], 2)

    check_statement("równania funkcyjne", ["f\(", "g\(", "funkcy?j"], 3, [not geo, not wielomian])

    check_solve("twierdzenie Bezout", ["b.zout"], 1, [wielomian])

    nierówność = False
    if count(["nierównoś"], statement) >= 1 or (count(["leq\s", "geq\s", "<", ">"], statement) >= 1 and count(["naturaln", "całkowit"], statement) == 0):
        nierówność = check_statement("nierówności", [], 0, [not geo, not zbiory, len(tags) < 2])

    check_solve("nierówności między średnimi", ["geometryczn", "harmoniczn", "arytmetyczn", "kwadratowa", "ważon", "średnimi", "ag", "kagh", "agh"], 3, [nierówność])

    check_solve("nierówność Cauchy'ego-Schwarza", ["schwarz"], 1, [nierówność])

    check_solve("twierdzenie o ciągach jednomonotonicznych", ["jednomonotoniczn"], 1, [nierówność, count(["ciąg"]) >= 1])

    check_solve("funkcje wypukłe", ["\swypukł"], 1, [not geo, count(["funkcj"]) >= 1, count(["kąt"], problem.statement) == 0])

    check_statement("nierówność Jensena", ["jensen"], 1)

    check_statement("granice ciągów", ["\sgranic", "lim\s"], 1, [len(tags) < 2])

    check_statement("równania", ["równanie", "równość", "="], 1, [len(tags) == 0])

    if len(tags) == 0:
        check_statement("brak tagów", [], 0)

    if len(solution) < 500:
        tags.clear()
        check_statement("za krótkie rozwiązanie", [], 0)

    tags.append(Tag.objects.get(name="AI"))

    return tags

def remove_tags(problem):
    for tag in problem.tag_set.all():
        if tag.type_id <= 4:
            problem.tag_set.remove(tag)

def attach_tags(problem):
    remove_tags(problem)
    for tag in deduce_tags(problem):
        problem.tag_set.add(tag)
    problem.save()

class Command(BaseCommand):
    help = "Tries to automatically deduce tags from problem's solution"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-i', '--id', type=int, help='Adds tags to given problem')
        group.add_argument('-a', '--all', help='Adds tags to all problems in db', action='store_true')
        group.add_argument('-s', '--solution', type=str, help='Prints tags for given solution')
        group.add_argument('-c', '--clear', help='Deletes all tags from all problems', action='store_true')

    def handle(self, *args, **kwargs):
        if kwargs['id']:
            try:
                problem = Problem.objects.get(id=kwargs['id'])
            except:
                raise CommandError('There is no problem with given id')
            attach_tags(problem)
        elif kwargs['all']:
            for problem in Problem.objects.all():
                attach_tags(problem)
        elif kwargs['solution']:
            tags = deduce_tags(kwargs['solution'])
            print(tags)
        elif kwargs['clear']:
            for problem in Problem.objects.all():
                remove_tags(problem)

# chcę dodać
# równania
# zespo do analizy
# granice

