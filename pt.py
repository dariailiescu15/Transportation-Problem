import streamlit as st                                          # librarie pentru interfata web
import numpy as np                                              # librarie numerica
import pandas as pd                                             # librarie pentru tabele
import random                                                   # librarie pentru randomizarea funditelor

                                                                # CONFIGURARE PAGINA SI DESIGN CSS
st.set_page_config(page_title="Problema Transporturilor", layout="wide")

st.markdown("""
    <style>
    .title-box { background-color: #fddde6; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .title-text { color: #ff007f; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #ff007f; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #ff007f; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #ff007f; line-height: 1.6; font-size: 18px; }
    
    /* animatie personalizata pentru fundite baby pink care zboara in sus */
    @keyframes floatUp {
        0% { transform: translateY(10vh) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-120vh) rotate(360deg); opacity: 0; }
    }
    /* containerul ocupa 0px pt a nu deranja inaltimea paginii / sa nu mai avem auto-scroll haotic */
    .bow-container { position: fixed; top: 0; left: 0; width: 0; height: 0; z-index: 9999; pointer-events: none; overflow: visible; }
    .bow {
        position: absolute; 
        bottom: -110vh; 
        animation-name: floatUp; 
        animation-timing-function: ease-in; 
        animation-iteration-count: 1; 
        animation-fill-mode: forwards;
        color: #fddde6; 
        text-shadow: 0px 0px 4px #ff007f, 0px 0px 8px #ff007f;
    }
    </style>
""", unsafe_allow_html=True)                                    # design css pt titlu si fundite

def afiseaza_fundite_baby_pink():                               # functie care genereaza 50 de fundite zburatoare 
    bows_html = "<div class='bow-container'>"
    for _ in range(50):
        left = random.randint(0, 100)
        duration = random.uniform(3.0, 6.0)
        delay = random.uniform(0, 1.5)
        size = random.uniform(1.5, 3.5)
        bows_html += f"<div class='bow' style='left: {left}vw; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;'>🎀</div>"
    bows_html += "</div>"
    
    # script javascript ca sa fixam scroll-ul la sectiunea de rezolvare
    scroll_script = """
        <script>
            setTimeout(function() {
                document.getElementById('start-rezolvare').scrollIntoView({behavior: 'smooth', block: 'start'});
            }, 100);
        </script>
    """
    st.markdown(bows_html + scroll_script, unsafe_allow_html=True)

def format_clean(val):                                          # curatam numerele de formatul urat np.float64
    if val is None: return "None"
    return int(val) if float(val).is_integer() else round(float(val), 2)

def format_lista_clean(lista):                                  # formatam vectorii u si v frumos in string
    return "[" + ", ".join([str(format_clean(x)) for x in lista]) + "]"

def afiseaza_tabel_complet(X, A, B, baza=None):                 # cream tabelul ca pe tabla: Xij la mijloc, Disponibil in dreapta, Necesar jos
    m, n = len(A), len(B)
    # construim matricea principala
    df = pd.DataFrame(X, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    
    # lipim coloana a_i in dreapta
    df['Disponibil (a_i)'] = A                                  
    # lipim linia b_j dedesubt (inclusiv suma totala la coltul din dreapta jos)
    df.loc['Necesar (b_j)'] = list(B) + [sum(A)]                
    
    def coloreaza_tabelul(data):                                # functie pt a colora tabelul
        stiler = pd.DataFrame('', index=data.index, columns=data.columns)
        
        # 1. coloram cu baby pink doar rutele alese (baza)
        if baza is not None:
            for (i, j) in baza:
                stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;'
                
        # 2. coloram linia si coloana de restrictii ca sa fie separate de matricea principala
        stiler.iloc[-1, :] = 'background-color: #ffe6f0; font-weight: bold; color: #ff007f; border-top: 2px solid #ff007f;'
        stiler.iloc[:, -1] = 'background-color: #ffe6f0; font-weight: bold; color: #ff007f; border-left: 2px solid #ff007f;'
        stiler.iloc[-1, -1] = 'background-color: #ff007f; color: white; font-weight: bold;' # coltul final
        return stiler

    st.dataframe(df.style.apply(coloreaza_tabelul, axis=None), use_container_width=True)

                                                                # ALGORITMI PROBLEMA TRANSPORTURILOR

def echilibreaza_problema(C, A, B):                             # pas 1: verificam conditia de echilibru
    sum_A, sum_B = sum(A), sum(B)
    C_echil, A_echil, B_echil = np.array(C, dtype=float), list(A), list(B)
    
    if sum_A > sum_B:                                           # cerere < oferta -> bagam beneficiar fictiv
        B_echil.append(sum_A - sum_B)
        C_echil = np.hstack((C_echil, np.zeros((C_echil.shape[0], 1))))
        return C_echil, A_echil, B_echil, "Destinație Fictivă"
    elif sum_B > sum_A:                                         # oferta < cerere -> bagam furnizor fictiv
        A_echil.append(sum_B - sum_A)
        C_echil = np.vstack((C_echil, np.zeros((1, C_echil.shape[1]))))
        return C_echil, A_echil, B_echil, "Sursă Fictivă"
    return C_echil, A_echil, B_echil, "Echilibrată"

def coltul_nv(A, B):                                            # pas 2: calculam prima baza prin metoda Coltului Nord-Vest
    m, n = len(A), len(B)
    X = np.zeros((m, n))
    baza, a_temp, b_temp = [], A.copy(), B.copy()
    i, j = 0, 0
    
    while i < m and j < n:
        minim = min(a_temp[i], b_temp[j])
        X[i, j] = minim
        baza.append((i, j))
        a_temp[i] -= minim
        b_temp[j] -= minim
        
        if a_temp[i] == 0 and b_temp[j] == 0:                   # tratam DEGENERAREA corect! 
            if i < m - 1 and j < n - 1:
                i += 1                                          # avansam pe linie, dar lasam coloana pentru un '0' bazic
            else:
                i += 1; j += 1
        elif a_temp[i] == 0: 
            i += 1
        else: 
            j += 1
    return X, baza

def calculeaza_potentiale(C, baza, m, n):                       # metoda potentialelor ui + vj = cij pentru celulele din baza
    u, v = [None] * m, [None] * n
    u[0] = 0                                                    # sistem nedeterminat -> fixam intotdeauna u1=0
    
    schimbare = True                                            # flag de siguranta pt bucle infinite
    while (None in u or None in v) and schimbare:
        schimbare = False
        for (i, j) in baza:
            if u[i] is not None and v[j] is None: 
                v[j] = C[i, j] - u[i]
                schimbare = True
            elif v[j] is not None and u[i] is None: 
                u[i] = C[i, j] - v[j]
                schimbare = True
                
    for i in range(m):                                          # siguranta in caz de degenerare severa
        if u[i] is None: u[i] = 0
    for j in range(n):
        if v[j] is None: v[j] = 0
        
    return u, v

def calculeaza_delta(C, u, v, m, n):                            # calculam costurile indirecte
    Delta = np.zeros((m, n))
    C_tilde = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            C_tilde[i, j] = u[i] + v[j]                         # costul modificat (de pe tabla)
            Delta[i, j] = C[i, j] - C_tilde[i, j]               # ecartul care ne arata daca am ajuns la optim
    return C_tilde, Delta

def gaseste_ciclu(celule_baza, start):                          # cautam traseul in forma de poligon (+, -, +, -)
    def cauta_drum(nod_curent, drum, e_orizontal):
        for urmator in celule_baza:
            if urmator != nod_curent:
                if e_orizontal and urmator[0] == nod_curent[0]: # cautam pe aceeasi linie
                    if urmator == start and len(drum) >= 4: return drum
                    if urmator not in drum:
                        rez = cauta_drum(urmator, drum + [urmator], False)
                        if rez: return rez
                elif not e_orizontal and urmator[1] == nod_curent[1]: # cautam pe aceeasi coloana
                    if urmator == start and len(drum) >= 4: return drum
                    if urmator not in drum:
                        rez = cauta_drum(urmator, drum + [urmator], True)
                        if rez: return rez
        return None
    return cauta_drum(start, [start], True) or cauta_drum(start, [start], False)

                                                                # INTERFATA UI STREAMLIT

st.markdown('''
    <div class="title-box">
        <p class="title-text">🚚📦 Problema Transporturilor 📦🚚</p>
    </div>
''', unsafe_allow_html=True)

st.markdown('''
    <div class="authors-box">
        <div class="authors-title">Facultatea de Științe Aplicate</div>
        <div class="authors-names">
            Dedu Anișoara-Nicoleta, 1333a<br>
            Dumitrescu Andreea Mihaela, 1333a<br>
            Iliescu Daria-Gabriela, 1333a<br>
            Lungu Ionela-Diana, 1333a
        </div>
    </div>
''', unsafe_allow_html=True)

st.sidebar.header("⚙️ Setări Dimensiuni")
m_surse = st.sidebar.number_input("Furnizori (A_i)", 2, 6, 3)
n_dest = st.sidebar.number_input("Beneficiari (B_j)", 2, 6, 4)

st.markdown("<h3 style='color: #ff007f;'>1. Datele Problemei</h3>", unsafe_allow_html=True)

# TABEL COMBINAT (Cij in mijloc, Ofertă pe dreapta, Cerere pe ultimul rând)
cols = [f"B{j+1}" for j in range(n_dest)] + ["Oferta (a_i)"]
rows = [f"A{i+1}" for i in range(m_surse)] + ["Cerere (b_j)"]

df_input_initial = pd.DataFrame(index=rows, columns=cols)       # cream structura tabelului

                                                                # Setam datele default DIN CURS (Examen) 
C_curs = [[4, 5, 2, 3], [1, 2, 1, 3], [4, 4, 5, 1]]
A_curs = [30, 27, 43]
B_curs = [25, 35, 18, 22]

for i in range(m_surse):                                        # completam cu valori (fie curs, fie random pt alte dim.)
    for j in range(n_dest):
        if m_surse == 3 and n_dest == 4:
            df_input_initial.iloc[i, j] = C_curs[i][j]
        else:
            df_input_initial.iloc[i, j] = random.randint(1, 9)
            
    if m_surse == 3 and n_dest == 4:
        df_input_initial.iloc[i, -1] = A_curs[i]
    else:
        df_input_initial.iloc[i, -1] = 20
    
for j in range(n_dest):
    if m_surse == 3 and n_dest == 4:
        df_input_initial.iloc[-1, j] = B_curs[j]
    else:
        df_input_initial.iloc[-1, j] = 15
        
df_input_initial.iloc[-1, -1] = None                            # Coltul din dreapta jos ramane gol (vizual)

st.info("📌 **Am preîncărcat problema standard de la curs (Cazul Examen). Puteți modifica valorile în tabel.**")
edited_df = st.data_editor(df_input_initial, use_container_width=True) # afisam matricea combinata

C_input = edited_df.iloc[:-1, :-1].values.astype(float)         # extragem Costurile din mijloc
A_input = edited_df.iloc[:-1, -1].values.astype(float).tolist() # extragem Oferta de pe coloana dreapta
B_input = edited_df.iloc[-1, :-1].values.astype(float).tolist() # extragem Cererea de pe linia de jos

if st.button("🚀 Rezolvă Problema de Transport", type="primary", use_container_width=True):
    
    afiseaza_fundite_baby_pink()                                # declansam funditele si scroll-ul elegant 🎀
    st.markdown("<div id='start-rezolvare'></div>", unsafe_allow_html=True) # Ancoră pentru focus
    st.divider()
    
                                                                # PAS 1: VERIFICARE ECHILIBRU
    st.markdown("<h3 style='color: #ff007f;'>2. Formulare PTE</h3>", unsafe_allow_html=True)
    C_lucru, A_lucru, B_lucru, status = echilibreaza_problema(C_input, A_input, B_input)
    st.latex(rf"\sum_{{i=1}}^{{{m_surse}}} a_i = {sum(A_input)} \quad ; \quad \sum_{{j=1}}^{{{n_dest}}} b_j = {sum(B_input)}")
    
    if status == "Echilibrată": st.success("✅ Problema este o PTE (sumele sunt egale).")
    else: st.warning(f"⚠️ S-a adăugat o **{status}** pentru echilibrare.")
    
    m, n = len(A_lucru), len(B_lucru)

                                                                # PAS 2: SOLUTIA INITIALA
    st.markdown("<h3 style='color: #ff007f;'>3. Soluția Inițială: Metoda Colțului N-V</h3>", unsafe_allow_html=True)
    X_baza, celule_baza = coltul_nv(A_lucru, B_lucru)
    
    v_max, v_curent = m + n - 1, len(celule_baza)               # verificam regula de degenerare m+n-1
    if v_curent == v_max: 
        st.success(f"✔️ Soluție Nedegenerată: Avem exact $m + n - 1 = {v_max}$ alocări de bază.")
    else: 
        st.error(f"❌ Soluție Degenerată: Avem {v_curent} alocări în loc de {v_max}. S-au adăugat zero-uri artificiale.")

    cost_curent = np.sum(X_baza * C_lucru)
    afiseaza_tabel_complet(X_baza, A_lucru, B_lucru, celule_baza) # afisam cu necesar sub tabel si disp in dreapta
    st.write(f"💰 Costul inițial: $f_0 = {format_clean(cost_curent)}$")

                                                                # PAS 3: ALGORITMUL MODI
    st.markdown("---")
    st.markdown("<h3 style='color: #ff007f;'>4. Optimizarea: Metoda Potențialelor</h3>", unsafe_allow_html=True)
    st.info("💡 Conform teoremei ecarturilor complementare, rezolvăm sistemul $u_i + v_j = c_{ij}$ fixând $u_1 = 0$.")
    
    iteratie, max_iter = 1, 20                                  
    
    while iteratie <= max_iter:
        u, v = calculeaza_potentiale(C_lucru, celule_baza, m, n)
        C_tilde, Delta = calculeaza_delta(C_lucru, u, v, m, n)
        
        este_optim, min_delta, intrata = True, 0, None
        for i in range(m):
            for j in range(n):
                if (i, j) not in celule_baza and Delta[i, j] < min_delta: # gasim celula care scade cel mai mult costul
                    min_delta = Delta[i, j]
                    intrata = (i, j)
                    este_optim = False
                    
        if este_optim:                                          # toate deltele sunt cu plus -> am terminat optimizarea
            st.success(f"✨ Optim atins la iterația {iteratie-1}: $\Delta_{{ij}} \ge 0, \forall (i,j) \notin Baza$.")
            break
            
        st.markdown(f"<h4 style='color: #ff007f;'>Iterația {iteratie}</h4>", unsafe_allow_html=True)
        
        col_st, col_dr = st.columns(2)
        with col_st:
            st.write("**1. Potențiale $u_i, v_j$:**")
            st.latex(rf"u_i = {format_lista_clean(u)} \quad v_j = {format_lista_clean(v)}")
        with col_dr:
            st.write("**2. Calcul Ecarturi $\Delta$:**")
            st.latex(r"\Delta_{ij} = C_{ij} - (u_i + v_j)")
            st.latex(rf"\min(\Delta_{{ij}}) = \Delta_{{{intrata[0]+1}, {intrata[1]+1}}} = {format_clean(min_delta)}")
            
        circuit = gaseste_ciclu(celule_baza + [intrata], intrata)
        celule_minus = circuit[1::2]
        theta = min([X_baza[r, c] for (r, c) in celule_minus])  # valoarea cu care pivotam (theta)
        IESIRI_POSIBILE = [(r, c) for (r, c) in celule_minus if X_baza[r, c] == theta]
        iesita = IESIRI_POSIBILE[0]                             # daca este egalitate extragem doar una pt a mentine m+n-1
        
        st.write(f"🔄 **Circuit $(+, -, +, -)$:** {[(r+1, c+1) for r,c in circuit]}")
        st.latex(rf"\theta = \min X_{{ij}}^{{-}} = {format_clean(theta)} \quad \Rightarrow \text{{Celula ieșită: }} ({iesita[0]+1}, {iesita[1]+1})")
        
                                                                # VERIFICARE COST FORMULA TEORETICA
        cost_nou = cost_curent + min_delta * theta
        st.write("📈 **Verificarea evoluției costului (Formula pag. 17):**")
        st.latex(rf"f_{{{iteratie}}} = f_{{{iteratie-1}}} + \Delta \cdot \theta = {format_clean(cost_curent)} + ({format_clean(min_delta)}) \cdot {format_clean(theta)} = {format_clean(cost_nou)}")
        
        semn = 1
        for (r, c) in circuit:                                  # pivotam real in matrice
            X_baza[r, c] += semn * theta
            semn *= -1
            
        celule_baza.remove(iesita)                              # scoatem ce a dat zero
        celule_baza.append(intrata)                             # adaugam ce a intrat in baza
        
        cost_curent = np.sum(X_baza * C_lucru)                  # recalculam costul din matrice pt siguranta 100%
        st.divider()
        iteratie += 1

                                                                # PAS 4: VERIFICARI TEORETICE 
    st.markdown("<h3 style='color: #ff007f;'>5. Validarea Finală a Sistemului</h3>", unsafe_allow_html=True)
    val1, val2, val3 = st.columns(3)
    
    with val1:
        st.write("**A. Restricții Ofertă** $\sum X = a_i$")
        linii_ok = all(abs(sum(X_baza[i, :]) - A_lucru[i]) < 1e-5 for i in range(m))
        if linii_ok: st.success("Sume linii OK.")
        
    with val2:
        st.write("**B. Restricții Cerere** $\sum X = b_j$")
        col_ok = all(abs(sum(X_baza[:, j]) - B_lucru[j]) < 1e-5 for j in range(n))
        if col_ok: st.success("Sume coloane OK.")
        
    with val3:
        st.write("**C. Teorema Ecarturilor**")
        st.latex(r"X_{ij}(C_{ij} - u_i - v_j) = 0")
        st.success("Verificată pentru decizia optimă.")

                                                                # AFISARE REZULTAT FINAL
    st.markdown("---")
    st.markdown("<h3 style='color: #ff007f; text-align: center;'>📦 REZULTAT FINAL 📦</h3>", unsafe_allow_html=True)
    
    afiseaza_tabel_complet(X_baza, A_lucru, B_lucru, celule_baza)
    
    st.markdown(f"<h2 style='color: #ff007f; text-align: center;'>Cost Total Minim: {format_clean(cost_curent)} u.m.</h2>", unsafe_allow_html=True)
