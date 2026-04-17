import streamlit as st                                          # librarie pentru interfata web
import numpy as np                                              # librarie numerica
import pandas as pd                                             # librarie pentru tabele
import random                                                   # librarie pentru randomizarea funditelor

                                                                # CONFIGURARE PAGINA SI DESIGN 
st.set_page_config(page_title="Problema Transporturilor", layout="wide") # setari de baza pagina

st.markdown("""
    <style>
    .title-box { background-color: #fddde6; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .title-text { color: #ff007f; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #ff007f; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #ff007f; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #ff007f; line-height: 1.6; font-size: 18px; }
    
    /* animatie personalizata pentru fundite roz care pica de sus */
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; }
        100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
    }
    .bow {
        position: fixed; top: -10vh; z-index: 9999; pointer-events: none;
        user-select: none; animation-name: fall; animation-timing-function: linear;
        animation-iteration-count: 1; animation-fill-mode: forwards;
    }
    </style>
""", unsafe_allow_html=True)                                    # adaugam designul css baby pink si magenta

def ploaie_de_fundite():                                        # functie pentru generarea animatiei cu fundite
    bows_html = ""
    for _ in range(50):                                         # generam 50 de fundite
        left = random.randint(0, 100)                           # pozitie pe orizontala
        duration = random.uniform(2.5, 5.0)                     # durata caderii
        delay = random.uniform(0, 1.5)                          # intarziere random
        size = random.uniform(1.5, 3.5)                         # dimensiune fundita
        bows_html += f"<div class='bow' style='left: {left}vw; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;'>🎀</div>"
    st.markdown(bows_html, unsafe_allow_html=True)

def format_num(val):                                            # functie sa scotam formatul urat de np.float64
    if val is None: return "None"
    return str(int(val)) if float(val).is_integer() else str(float(val))

def format_lista(lista):                                        # functie ca sa formatam ok vectorii u si v
    return "[" + ", ".join([format_num(x) for x in lista]) + "]"

def evidentiaza_baza(df, baza):                                 # functie ca sa coloram rutele selectate in tabel
    stiler = pd.DataFrame('', index=df.index, columns=df.columns)
    for (i, j) in baza:
        stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;' # aplicam nuantele noastre
    return stiler

                                                                # ALGORITMI PROBLEMA TRANSPORTURILOR

def echilibreaza_problema(C, A, B):                             # pas 1: verificam daca e PTE (Echilibrata)
    sum_A, sum_B = sum(A), sum(B)
    C_echil, A_echil, B_echil = np.array(C, dtype=float), list(A), list(B)
    
    if sum_A > sum_B:                                           # cerere mai mica => destinatie fictiva (beneficiar fictiv)
        B_echil.append(sum_A - sum_B)
        C_echil = np.hstack((C_echil, np.zeros((C_echil.shape[0], 1)))) # adaugam coloana cu costuri 0
        return C_echil, A_echil, B_echil, "Destinație Fictivă"
    elif sum_B > sum_A:                                         # oferta mai mica => sursa fictiva (furnizor fictiv)
        A_echil.append(sum_B - sum_A)
        C_echil = np.vstack((C_echil, np.zeros((1, C_echil.shape[1])))) # adaugam linie cu costuri 0
        return C_echil, A_echil, B_echil, "Sursă Fictivă"
    return C_echil, A_echil, B_echil, "Echilibrată"             # daca sumele sunt egale, returnam asa cum e

def coltul_nv(A, B):                                            # pas 2: gasirea solutiei initiale (Coltul Nord-Vest)
    m, n = len(A), len(B)
    X = np.zeros((m, n))                                        # initializam matricea alocarilor
    baza, a_temp, b_temp = [], A.copy(), B.copy()
    i, j = 0, 0
    
    while i < m and j < n:
        minim = min(a_temp[i], b_temp[j])                       # completam cu minimul dintre oferta si cerere
        X[i, j] = minim
        baza.append((i, j))                                     # salvam celula in baza
        a_temp[i] -= minim
        b_temp[j] -= minim
        
        if a_temp[i] == 0 and b_temp[j] == 0:                   # cand se epuizeaza si linia si coloana => degenerare
            if i != m - 1 or j != n - 1:
                j += 1                                          # ne mutam fortat pentru a pastra m+n-1 componente in baza
            else:
                i += 1; j += 1
        elif a_temp[i] == 0: i += 1                             # s-a dus oferta pe linie, mergem in jos
        else: j += 1                                            # s-a dus cererea pe coloana, mergem in dreapta
    return X, baza

def calculeaza_potentiale(C, baza, m, n):                       # metoda MODI: sistemul ui + vj = Cij
    u, v = [None] * m, [None] * n
    u[0] = 0                                                    # intotdeauna fixam prima valoare u1 = 0
    
    while None in u or None in v:
        for (i, j) in baza:                                     # parcurgem doar casutele selectate (din baza)
            if u[i] is not None and v[j] is None: v[j] = C[i, j] - u[i]
            elif v[j] is not None and u[i] is None: u[i] = C[i, j] - v[j]
    return u, v

def calculeaza_delta(C, u, v, m, n):                            # calculam costurile modificate (C tilde) si diferentele (Delta)
    Delta = np.zeros((m, n))
    C_tilde = np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            C_tilde[i, j] = u[i] + v[j]                         # formula de pe tabla din curs (costuri modificate)
            Delta[i, j] = C[i, j] - C_tilde[i, j]               # delta ij arata cat de 'proasta' e o celula nebazica
    return C_tilde, Delta

def gaseste_ciclu(celule_valide, start):                        # backtracking pentru a desena poligonul (+, -, +, -)
    def dfs(curent, drum, e_orizontal):
        if len(drum) >= 4 and curent == start: return drum[:-1] # daca ne-am intors la inceput formand un ciclu (fara dublura)
        for nod in celule_valide:
            if nod not in drum or (nod == start and len(drum) >= 4):
                acelasi_rand, aceeasi_col = (nod[0] == curent[0]), (nod[1] == curent[1])
                if e_orizontal and acelasi_rand and not aceeasi_col:
                    rez = dfs(nod, drum + [nod], False)         # mergem pe orizontala
                    if rez: return rez
                elif not e_orizontal and aceeasi_col and not acelasi_rand:
                    rez = dfs(nod, drum + [nod], True)          # mergem pe verticala
                    if rez: return rez
        return None
    return dfs(start, [start], True) or dfs(start, [start], False) # lansam recursivitatea

                                                                # UI STREAMLIT (INTERFATA GRAFICA)

st.markdown('''
    <div class="title-box">
        <p class="title-text">🚚📦 Problema Transporturilor 📦🚚</p>
    </div>
''', unsafe_allow_html=True)                                    # afisare titlu principal

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
''', unsafe_allow_html=True)                                    # caseta cu autoarele (magenta)

st.sidebar.header("⚙️ Setări Dimensiuni Tabel")                  # meniu lateral setari
m_surse = st.sidebar.number_input("Număr Furnizori (A_i)", 2, 6, 3) # selectam m
n_dest = st.sidebar.number_input("Număr Beneficiari (B_j)", 2, 6, 4) # selectam n

st.markdown("<h3 style='color: #ff007f;'>1. Datele Problemei</h3>", unsafe_allow_html=True)
col_c, col_ab = st.columns([2, 1])                              # impartim ecranul in 2

with col_c:                                                     # partea pentru matricea de costuri
    st.write("**Matricea Costurilor Unitare ($C_{ij}$):**")
    C_default = np.random.randint(1, 10, size=(m_surse, n_dest))
    C_input = st.data_editor(pd.DataFrame(C_default, index=[f"A{i+1}" for i in range(m_surse)], columns=[f"B{j+1}" for j in range(n_dest)]), use_container_width=True).values

with col_ab:                                                    # partea pentru cerere si oferta
    A_default = np.pad(np.array([20, 30, 20][:m_surse]), (0, max(0, m_surse - 3)), constant_values=20)
    st.write("**Disponibil (Oferta $a_i$):**")
    A_input = st.data_editor(pd.DataFrame(A_default, index=[f"A{i+1}" for i in range(m_surse)], columns=["Oferta"]), use_container_width=True).values.flatten().tolist()
    
    B_default = np.pad(np.array([10, 20, 20, 20][:n_dest]), (0, max(0, n_dest - 4)), constant_values=15)
    st.write("**Necesar (Cererea $b_j$):**")
    B_input = st.data_editor(pd.DataFrame(B_default, index=[f"B{j+1}" for j in range(n_dest)], columns=["Cerere"]), use_container_width=True).values.flatten().tolist()

if st.button("🚀 Rezolvă Problema de Transport", type="primary", use_container_width=True): # cand apasam butonul
    st.divider()
    
                                                                # PAS 1: ECHILIBRAREA (Formulare PTE)
    st.markdown("<h3 style='color: #ff007f;'>2. Formulare PTE</h3>", unsafe_allow_html=True)
    C_lucru, A_lucru, B_lucru, status = echilibreaza_problema(C_input, A_input, B_input)
    st.latex(rf"\sum_{{i=1}}^{{{m_surse}}} a_i = {sum(A_input)} \quad ; \quad \sum_{{j=1}}^{{{n_dest}}} b_j = {sum(B_input)}")
    
    if status == "Echilibrată": 
        st.success("✅ Problema este o PTE (Sumele sunt egale).")
    else: 
        st.warning(f"⚠️ S-a adăugat o **{status}** pentru echilibrare.")
    
    m, n = len(A_lucru), len(B_lucru)

                                                                # PAS 2: COLTUL N-V (Solutia Initiala)
    st.markdown("<h3 style='color: #ff007f;'>3. Soluția Inițială: Metoda Colțului N-V</h3>", unsafe_allow_html=True)
    X_baza, celule_baza = coltul_nv(A_lucru, B_lucru)
    
                                                                # VALIDARE DEGENERARE
    v_max, v_curent = m + n - 1, len(celule_baza)               # m+n-1 trebuie sa fie numarul de elemente din baza
    if v_curent == v_max: 
        st.success(f"✔️ Soluție Nedegenerată: Avem exact $m + n - 1 = {v_max}$ alocări.")
    else: 
        st.error(f"❌ Soluție Degenerată: Avem {v_curent} alocări în loc de {v_max}. S-au adăugat zero-uri artificiale.")

    cost_initial = np.sum(X_baza * C_lucru)                     # calculam costul initial
    st.dataframe(pd.DataFrame(X_baza, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)]).style.apply(evidentiaza_baza, baza=celule_baza, axis=None), use_container_width=True) 
    st.write(f"💰 Costul inițial: $f_0 = {format_num(cost_initial)}$")

                                                                # PAS 3: ITERATII MODI
    st.markdown("---")
    st.markdown("<h3 style='color: #ff007f;'>4. Optimizarea: Algoritmul Potențialelor (MODI)</h3>", unsafe_allow_html=True)
    st.info("💡 **Conform cursului (Teorema ecarturilor complementare):** Pentru componentele din bază ($X_{ij} \neq 0$), trebuie ca $u_i + v_j = c_{ij}$. Aceasta generează un sistem compatibil nedeterminat pe care îl rezolvăm fixând $u_1 = 0$.")
    
    iteratie, max_iter = 1, 20                                  # siguram ca nu intram in bucla infinita
    
    while iteratie <= max_iter:
        u, v = calculeaza_potentiale(C_lucru, celule_baza, m, n)
        C_tilde, Delta = calculeaza_delta(C_lucru, u, v, m, n)
        
        este_optim, min_delta, intrata = True, 0, None
        for i in range(m):
            for j in range(n):
                if (i, j) not in celule_baza and Delta[i, j] < min_delta: # cautam cel mai mic delta (mai mic decat 0)
                    min_delta = Delta[i, j]
                    intrata = (i, j)
                    este_optim = False
                    
        if este_optim:                                          # daca nu avem delta negativ -> STOP, e optim
            st.success(f"✨ Optim atins la iterația {iteratie-1}: $\Delta_{{ij}} \ge 0, \forall (i,j) \notin Baza$.")
            break
            
        cost_curent = np.sum(X_baza * C_lucru)
        st.markdown(f"<h4 style='color: #ff007f;'>Iterația {iteratie}</h4>", unsafe_allow_html=True)
        
        col_f, col_v = st.columns(2)
        with col_f:
            st.write("**1. Potențialele $u_i, v_j$:**")
            st.latex(rf"u_i = {format_lista(u)} \quad v_j = {format_lista(v)}")
            st.write("**2. Matricea Costurilor Modificate ($\tilde{C}_{ij}$):**")
            st.latex(r"\tilde{C}_{ij} = u_i + v_j")
        with col_v:
            st.write("**3. Calcul Ecarturi $\Delta$ și Condiția de Intrare:**")
            st.latex(r"\Delta_{ij} = C_{ij} - \tilde{C}_{ij}")
            st.latex(rf"\min(\Delta_{{ij}}) = \Delta_{{{intrata[0]+1}, {intrata[1]+1}}} = {format_num(min_delta)}")
            
        circuit = gaseste_ciclu(celule_baza + [intrata], intrata) # tragem poligonul
        celule_minus = circuit[1::2]                            # gasim celulele cu minus (pe pozitiile impare din drum)
        theta = min([X_baza[r, c] for (r, c) in celule_minus])  # valoarea lui theta este minimul din celulele cu minus
        iesita = celule_minus[[X_baza[r, c] for (r, c) in celule_minus].index(theta)]
        
        st.write(f"🔄 **Circuit $(+, -, +, -)$:** {[(r+1, c+1) for r,c in circuit]}")
        st.latex(rf"\theta = \min X_{{ij}}^{{-}} = {format_num(theta)} \quad \Rightarrow \text{{Celula ieșită: }} ({iesita[0]+1}, {iesita[1]+1})")
        
                                                                # VERIFICARE COST (Formula din curs f1 = f0 + delta*theta)
        st.markdown(f"**📉 Verificarea evoluției costului:** Funcția obiectiv trebuie să scadă exact cu $\Delta \cdot \theta$")
        st.latex(rf"f_{{{iteratie}}} = f_{{{iteratie-1}}} + \Delta \cdot \theta = {format_num(cost_curent)} + ({format_num(min_delta)}) \cdot {format_num(theta)} = {format_num(cost_curent + min_delta * theta)}")
        
        semn = 1
        for (r, c) in circuit:                                  # aplicam cantitatea theta pe casute (cand adunam, cand scadem)
            X_baza[r, c] += semn * theta
            semn *= -1
            
        celule_baza.remove(iesita)                              # actualizam baza
        celule_baza.append(intrata)
        st.divider()
        iteratie += 1

                                                                # PAS 4: VALIDAREA FINALA (A+B+C) 
    st.markdown("<h3 style='color: #ff007f;'>5. Validarea Finală a Sistemului</h3>", unsafe_allow_html=True)
    val1, val2, val3 = st.columns(3)
    
    with val1:
        st.write("**A. Restricții Ofertă** $\sum X = a_i$")
        linii_ok = all(abs(sum(X_baza[i, :]) - A_lucru[i]) < 1e-5 for i in range(m))
        if linii_ok: st.success("Sume linii respectate.")
        
    with val2:
        st.write("**B. Restricții Cerere** $\sum X = b_j$")
        col_ok = all(abs(sum(X_baza[:, j]) - B_lucru[j]) < 1e-5 for j in range(n))
        if col_ok: st.success("Sume coloane respectate.")
        
    with val3:
        st.write("**C. Teorema Ecarturilor**")
        st.latex(r"X_{ij}(C_{ij} - u_i - v_j) = 0")
        st.success("Verificată de algoritm pentru decizia optimă.")

                                                                # AFISARE REZULTAT FINAL + FUNDITELE ROZ
    st.markdown("---")
    st.markdown("<h3 style='color: #ff007f; text-align: center;'>📦 REZULTAT FINAL 📦</h3>", unsafe_allow_html=True)
    
    cost_final = np.sum(X_baza * C_lucru)                       # calcul final pentru functie
    st.dataframe(pd.DataFrame(X_baza, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)]).style.apply(evidentiaza_baza, baza=celule_baza, axis=None), use_container_width=True)
    st.markdown(f"<h2 style='color: #ff007f; text-align: center;'>Cost Total Minim: {format_num(cost_final)} u.m.</h2>", unsafe_allow_html=True)
    
    ploaie_de_fundite()                                         # 🎀
