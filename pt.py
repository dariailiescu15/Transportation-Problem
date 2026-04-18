import streamlit as st                                          # importam libraria principala pt a face interfata web
import numpy as np                                              # libraria pt calcule matematice cu matrice
import pandas as pd                                             # libraria asta ne ajuta sa afisam tabelele frumos
import random                                                   # ne trebuie pt a genera funditele aleatoriu pe ecran

                                                                # CONFIGURARE PAGINA SI DESIGN CSS
st.set_page_config(page_title="Problema Transporturilor", layout="wide") # setam pagina sa ocupe tot ecranul

st.markdown("""
    <style>
    /* aici am bagat niste CSS ca sa fac titlul roz si sa arate mai dragut proiectul */
    .title-box { background-color: #fddde6; border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2); }
    .title-text { color: #ff007f; font-size: 55px; font-weight: 900; margin: 0; font-family: 'Segoe UI', sans-serif; }
    .authors-box { color: #ff007f; text-align: right; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    .authors-title { color: #ff007f; font-weight: bold; font-style: italic; font-size: 20px; margin-bottom: 8px; }
    .authors-names { color: #ff007f; line-height: 1.6; font-size: 18px; }
    
    /* animatie pentru fundite baby pink care cad de sus cand apasam butonul de rezolvare */
    @keyframes fallDown {
        0% { top: -100px; transform: rotate(0deg); opacity: 1; }
        100% { top: 100vh; transform: rotate(360deg); opacity: 0; }
    }
    .bow {
        position: fixed; z-index: 99999; pointer-events: none; user-select: none; 
        animation-name: fallDown; animation-timing-function: linear; 
        animation-iteration-count: 1; animation-fill-mode: forwards;
        color: #fddde6; text-shadow: 0px 0px 4px #ff007f, 0px 0px 8px #ff007f;
    }
    </style>
""", unsafe_allow_html=True)                                    # trebuie activat html-ul ca sa mearga css-ul de mai sus

def afiseaza_fundite_baby_pink():                               # functia mea care genereaza 50 de fundite zburatoare
    bows_html = "<div style='position: fixed; top: 0; left: 0; width: 0px; height: 0px; pointer-events: none; z-index: 99999; overflow: visible;'>"
    for _ in range(50):
        left = random.randint(0, 100)                           # pica de la pozitii random pe axa X
        duration = random.uniform(3.0, 6.0)                     # unele pica mai repede, altele mai incet
        delay = random.uniform(0, 1.5)
        size = random.uniform(1.5, 3.5)
        bows_html += f"<div class='bow' style='left: {left}vw; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;'>🎀</div>"
    bows_html += "</div>"
    st.markdown(bows_html, unsafe_allow_html=True)              # le afisez efectiv in interfata

def fmt(val):                                                   # functie salvatoare pt a scapa de zecimale inutile gen 25.0000 
    if pd.isna(val) or val is None: return ""                   # daca e gol, returnam string gol
    if isinstance(val, (np.floating, float, int)):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}" # lasa intreg daca e intreg, altfel doar 2 zecimale
    return str(val)

def afiseaza_tabel_x(X, m, n, baza=None):                       # functie pe care o folosesc ca sa afisez tabelele intermediare (T0, T1, etc)
    df = pd.DataFrame(X, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    for col in df.columns: df[col] = df[col].apply(fmt)         # curatam fiecare celula
        
    def coloreaza_baza(data):                                   # functie pt culori
        stiler = pd.DataFrame('', index=data.index, columns=data.columns)
        if baza is not None:
            for (i, j) in baza:
                stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;' # colorez celulele de baza cu roz
        return stiler
    st.dataframe(df.style.apply(coloreaza_baza, axis=None))     # afisam tabelul in aplicatie

def afiseaza_tabel_final(X, A, B, baza=None):                   # functia asta afiseaza fix ultimul tabel, ala mare si frumos
    m, n = len(A), len(B)
    df = pd.DataFrame(X, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    df['Disp. (a_i)'] = [fmt(x) for x in A]                     # adaug coloana pt disponibilitati            
    df.loc['Necesar (b_j)'] = [fmt(x) for x in B] + [fmt(sum(A))] # adaug linia pt necesar si total
    for col in df.columns: df[col] = df[col].apply(fmt)

    def coloreaza_mixt(data):                                   
        stiler = pd.DataFrame('', index=data.index, columns=data.columns)
        if baza is not None:
            for (i, j) in baza:
                stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;' # roz pt baza
        stiler.iloc[-1, :] = 'background-color: #d4edda; font-weight: bold; color: #155724; border-top: 2px solid #28a745;' # verde jos
        stiler.iloc[:, -1] = 'background-color: #d4edda; font-weight: bold; color: #155724; border-left: 2px solid #28a745;' # verde dreapta
        stiler.iloc[-1, -1] = 'background-color: #28a745; color: white; font-weight: bold;' # coltul dreapta-jos super verde
        return stiler
    st.dataframe(df.style.apply(coloreaza_mixt, axis=None), use_container_width=True)

                                                                # =======================================================
                                                                # LOGICA MATEMATICA: ALGORITMI PROBLEMA TRANSPORTURILOR
                                                                # =======================================================

def echilibreaza_problema(C, A, B):                             # PAS 1: verific daca Suma Oferta == Suma Cerere
    sum_A, sum_B = sum(A), sum(B)
    C_echil, A_echil, B_echil = np.array(C, dtype=float), list(A), list(B)
    
    if sum_A > sum_B:                                           # daca avem prea multa marfa -> bagam un beneficiar fals
        B_echil.append(sum_A - sum_B)
        C_echil = np.hstack((C_echil, np.zeros((C_echil.shape[0], 1)))) # costurile catre el sunt 0 evident
        return C_echil, A_echil, B_echil, "Beneficiar Fictiv B*"
    elif sum_B > sum_A:                                         # daca e cerere prea mare -> bagam un furnizor fals
        A_echil.append(sum_B - sum_A)
        C_echil = np.vstack((C_echil, np.zeros((1, C_echil.shape[1]))))
        return C_echil, A_echil, B_echil, "Furnizor Fictiv A*"
    return C_echil, A_echil, B_echil, "Echilibrată"             # daca sunt egale, e perfect, nu facem nimic

def coltul_nv(A, B):                                            # PAS 2: aflu prima solutie de baza folosind Coltul Nord-Vest
    m, n = len(A), len(B)
    X = np.zeros((m, n))                                        # matricea cu cantitati (initial totul e 0)
    baza, a_temp, b_temp = [], list(A), list(B)
    i, j = 0, 0
    
    while i < m and j < n:                                      # parcurgem tabelul de la stanga-sus spre dreapta-jos
        minim = min(a_temp[i], b_temp[j])                       # luam cantitatea maxima posibila (minimul dintre ce am si ce se cere)
        X[i, j] = minim
        baza.append((i, j))                                     # salvez coordonatele in lista celulelor de baza
        a_temp[i] -= minim
        b_temp[j] -= minim
        
        if a_temp[i] == 0 and b_temp[j] == 0:                   # ASTA E IMPORTANT: tratam cazurile degenerate direct din algoritm
            if j < n - 1: j += 1
            elif i < m - 1: i += 1
            else: break
        elif a_temp[i] == 0: i += 1                             # mutam randul
        else: j += 1                                            # mutam coloana
    return X, baza

def calculeaza_potentiale(C, baza, m, n):                       # pt METODA MODI: rezolvam sistemul u_i + v_j = c_ij
    u, v = [None] * m, [None] * n
    u[0] = 0                                                    # fixam noi u1=0 pt ca sistemul are prea putine ecuatii altfel (nedeterminat)
    
    schimbare = True                                            
    while (None in u or None in v) and schimbare:               # rulam pana gasim toate u-urile si v-urile
        schimbare = False
        for (i, j) in baza:
            if u[i] is not None and v[j] is None: 
                v[j] = C[i, j] - u[i]; schimbare = True         # daca stiu u, il aflu pe v
            elif v[j] is not None and u[i] is None: 
                u[i] = C[i, j] - v[j]; schimbare = True         # daca stiu v, il aflu pe u
                
    for i in range(m):
        if u[i] is None: u[i] = 0                               # masura de siguranta in caz de probleme de blocaj
    for j in range(n):
        if v[j] is None: v[j] = 0
    return u, v

def calculeaza_delta(C, u, v, m, n):                            # tot pt MODI: calculez costurile C-tilde si apoi Ecarturile (Delta)
    Delta, C_tilde = np.zeros((m, n)), np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            C_tilde[i, j] = u[i] + v[j]                         # costul teoretic
            Delta[i, j] = C[i, j] - C_tilde[i, j]               # cat de mult pierdem/castigam (Ecartul)
    return C_tilde, Delta

def gaseste_ciclu(celule_baza, start):                          # o functie care cauta traseul in forma de poligon (+, -, +, -) cand pivotam
    def cauta_drum(nod_curent, drum, e_orizontal):
        for urmator in celule_baza:
            if urmator != nod_curent:
                if e_orizontal and urmator[0] == nod_curent[0]: 
                    if urmator == start and len(drum) >= 4: return drum     # m-am intors la inceput!
                    if urmator not in drum:
                        rez = cauta_drum(urmator, drum + [urmator], False)  # schimb directia pe verticala
                        if rez: return rez
                elif not e_orizontal and urmator[1] == nod_curent[1]: 
                    if urmator == start and len(drum) >= 4: return drum
                    if urmator not in drum:
                        rez = cauta_drum(urmator, drum + [urmator], True)   # schimb directia pe orizontala
                        if rez: return rez
        return None
    return cauta_drum(start, [start], True) or cauta_drum(start, [start], False)

                                                                # =======================================================
                                                                # INTERFATA UI STREAMLIT (Aici cream efectiv butoanele)
                                                                # =======================================================

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

st.sidebar.header("⚙️ Setări Dimensiuni")                       # meniul din stanga pt a schimba dimensiunea matricii
m_surse = st.sidebar.number_input("Furnizori (A_i)", 2, 6, 3)
n_dest = st.sidebar.number_input("Beneficiari (B_j)", 2, 6, 4)

st.markdown("<h3 style='color: #ff007f;'>📝 Datele Problemei</h3>", unsafe_allow_html=True)

# ==============================================================================
# TABEL DE INTRARE (Salvat in memoria aplicatiei ca sa nu se mai reseteze la editare)
# ==============================================================================
def genereaza_date_initiale(m, n):
    cols = [f"B{j+1}" for j in range(n)] + ["Oferta (a_i)"]
    rows = [f"A{i+1}" for i in range(m)] + ["Cerere (b_j)"]
    # FORTAM tabelul sa fie format din cifre (float), ca sa nu ne mai blocheze editarea
    df = pd.DataFrame(index=rows, columns=cols, dtype=float)       

    # Datele noastre initiale din Ex 1
    C_curs = [[1, 3, 2, 4], [3, 1, 2, 2], [2, 3, 2, 1]]
    A_curs = [30, 39, 21]
    B_curs = [25, 20, 30, 15]

    for i in range(m):                                        
        for j in range(n):
            if m == 3 and n == 4: df.iloc[i, j] = C_curs[i][j]
            else: df.iloc[i, j] = random.randint(1, 9)
                
        if m == 3 and n == 4: df.iloc[i, -1] = A_curs[i]
        else: df.iloc[i, -1] = 20
        
    for j in range(n):
        if m == 3 and n == 4: df.iloc[-1, j] = B_curs[j]
        else: df.iloc[-1, j] = 15
            
    # In loc de None, punem 0.0 ca sa pastram coloana matematica
    df.iloc[-1, -1] = 0.0                            
    return df

# AICI E SECRETUL: Salvam tabelul in session_state (memoria interna)
# Se va schimba DOAR DACA utilizatorul modifica numarul de furnizori/beneficiari din meniul stanga
if "tabel_date" not in st.session_state or st.session_state.get("m_vechi") != m_surse or st.session_state.get("n_vechi") != n_dest:
    st.session_state.tabel_date = genereaza_date_initiale(m_surse, n_dest)
    st.session_state.m_vechi = m_surse
    st.session_state.n_vechi = n_dest

def coloreaza_input(data):                                      # gri pt linia de jos si coloana din dreapta
    stiler = pd.DataFrame('', index=data.index, columns=data.columns)
    stiler.iloc[-1, :] = 'background-color: #f0f2f6; font-weight: bold; border-top: 2px solid #555;'
    stiler.iloc[:, -1] = 'background-color: #f0f2f6; font-weight: bold; border-left: 2px solid #555;'
    # Smecherie vizuala: facem textul din colt de aceeasi culoare cu fundalul ca sa ascundem acel 0.0
    stiler.iloc[-1, -1] = 'background-color: #e0e4eb; color: #e0e4eb;'          
    return stiler

st.write("**Introduceți Costurile Unitare ($c_{ij}$), Oferta și Cererea:**")

# Parametrul "key" blocheaza resetarea tabelului cand dam click pe el
edited_df = st.data_editor(
    st.session_state.tabel_date.style.apply(coloreaza_input, axis=None), 
    use_container_width=True,
    key="editor_problema"
) 

# Extrag valorile din tabelul editat pt calcule
C_input = edited_df.iloc[:-1, :-1].values.astype(float)         
A_input = edited_df.iloc[:-1, -1].values.astype(float).tolist() 
B_input = edited_df.iloc[-1, :-1].values.astype(float).tolist()

# Cand apasam butonul incepe MAGIA
if st.button("🚀 Rezolvă Problema Pas cu Pas", type="primary", use_container_width=True):
    
    afiseaza_fundite_baby_pink()                                # pornim ploaia de fundite
    st.divider()
    
    # --------------------------------------------------------- PASUL 1: ECHILIBRUL -----------------------
    st.markdown("<h3 style='color: #ff007f;'>Pasul 1. Verificăm dacă avem PTE</h3>", unsafe_allow_html=True)
    C_lucru, A_lucru, B_lucru, status = echilibreaza_problema(C_input, A_input, B_input)
    
    sum_A, sum_B = sum(A_input), sum(B_input)
    st.latex(rf"\Sigma D = {fmt(sum_A)} \quad ; \quad \Sigma N = {fmt(sum_B)}") # afisez frumos ecuatiile
    
    if status == "Echilibrată": 
        st.latex(r"\Sigma D = \Sigma N \Rightarrow \text{avem PTE}")
    else: 
        st.warning(rf"⚠️ $\Sigma D \neq \Sigma N$. Se introduce un **{status}** cu costuri de transport $c_{{ij}} = 0$.")
    
    m, n = len(A_lucru), len(B_lucru)

    # --------------------------------------------------------- PASUL 2: COLTUL N-V -----------------------
    st.markdown("<h3 style='color: #ff007f;'>Pasul 2. Metoda Colțului N-V</h3>", unsafe_allow_html=True)
    st.write("Aplicăm metoda Colțului N-V și completăm tabelul $T_0$:")
    
    X_baza, celule_baza = coltul_nv(A_lucru, B_lucru)
    afiseaza_tabel_x(X_baza, m, n, celule_baza)
    
    v_max, v_curent = m + n - 1, len(celule_baza)               # nr. de variabile de baza teoretic vs real
    st.latex(rf"V = m + n - 1 = {m} + {n} - 1 = {v_max}")
    st.latex(rf"NC = \text{{nr. celule completate in }} T_0 = {v_curent}")
    
    if v_curent == v_max: 
        st.success(r"$NC = V \Rightarrow$ soluție **nedegenerată**. Continuăm rezolvarea.")
    else: 
        st.error(r"$NC < V \Rightarrow$ soluție **degenerată**. S-au adăugat alocări de 0 pentru perturbare ($\epsilon$).")

    # Aflam cat ne-ar costa transportul acum la inceput
    cost_curent = np.sum(X_baza * C_lucru)
    formule_f0 = [rf"{fmt(C_lucru[i,j])} \cdot {fmt(X_baza[i,j])}" for (i,j) in celule_baza]
    st.latex(r"f_0 = f_{min}(X^0) = \sum c_{ij} \cdot X_{ij} = " + " + ".join(formule_f0) + rf" = {fmt(cost_curent)}")

    # --------------------------------------------------------- PASUL 3: MODI (POTENTIALE) ----------------
    st.divider()
    st.markdown("<h3 style='color: #ff007f;'>Pasul 3. Aplicăm TO (Testul de Optimalitate)</h3>", unsafe_allow_html=True)
    
    iteratie, max_iter = 0, 15                                  # protectie: nu rulam la infinit daca se blocheaza
    
    while iteratie < max_iter:
        # Afisam titlul iteratiei ca in seminar (ex: Iterația I_0 (T_0, X_0, f_0))
        st.markdown(rf"#### Iterația $I_{{{iteratie}}}$ ($T_{{{iteratie}}}$, $X_{{{iteratie}}}$, $f_{{{iteratie}}}$)")
        
        # Pagina 6 din pdf: Sistemul S
        u, v = calculeaza_potentiale(C_lucru, celule_baza, m, n)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(r"**① Sistemul $S: u_i + v_j = c_{ij}$**")
            sistem_latex = r"\begin{cases} "
            for (i, j) in celule_baza:
                sistem_latex += rf"u_{{{i+1}}} + v_{{{j+1}}} = {fmt(C_lucru[i,j])} \\ "
            sistem_latex += r"\end{cases}"
            st.latex(sistem_latex)                              # generez acolada aia mare cu ecuatii
        
        with col2:
            st.markdown(r"**Alegem $u_1 = 0 \Rightarrow$**")
            rez_latex = r"\begin{cases} "
            for i in range(m): rez_latex += rf"u_{{{i+1}}} = {fmt(u[i])} \\ "
            for j in range(n): rez_latex += rf"v_{{{j+1}}} = {fmt(v[j])} \\ "
            rez_latex += r"\end{cases}"
            st.latex(rez_latex)

        # Tabelele din pagina 7 si 8: C cu tilda si Delta
        C_tilde, Delta = calculeaza_delta(C_lucru, u, v, m, n)
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(r"**② Tabel $\tilde{C} \Rightarrow \tilde{C}_{ij} = u_i + v_j$**")
            df_ctilde = pd.DataFrame(C_tilde, index=[f"{fmt(u[i])}=u{i+1}" for i in range(m)], columns=[f"v{j+1}={fmt(v[j])}" for j in range(n)])
            for col in df_ctilde.columns: df_ctilde[col] = df_ctilde[col].apply(fmt)
            st.dataframe(df_ctilde)
            
        with col4:
            st.markdown(r"**③ Tabel $\Delta \Rightarrow \delta_{ij} = c_{ij} - \tilde{C}_{ij}$**")
            df_delta = pd.DataFrame(Delta, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
            
            def style_delta(data):                              # fac rosu doar unde e delta negativ, adica fix unde ne doare
                stiler = pd.DataFrame('', index=data.index, columns=data.columns)
                for r in data.index:
                    for c in data.columns:
                        if data.loc[r, c] < 0:
                            stiler.loc[r, c] = 'background-color: #ffcccc; color: red; font-weight: bold;'
                return stiler
            st.dataframe(df_delta.style.apply(style_delta, axis=None))

        # Pagina 8 jos: Verificam daca TO e indeplinit (toate Delta-urile >= 0)
        este_optim, min_delta, intrata = True, 0, None
        for i in range(m):
            for j in range(n):
                if (i, j) not in celule_baza and Delta[i, j] < min_delta: 
                    min_delta = Delta[i, j]
                    intrata = (i, j)                            # salvez coordonatele unde am gasit "buba" (valoarea negativa)
                    este_optim = False
                    
        if este_optim:
            # STOP JOC, am ajuns la cel mai bun cost!
            st.success(rf"**④ $TO: \forall \delta_{{ij}} \ge 0 \Rightarrow DA \Rightarrow STOP \Rightarrow I_{{STOP}} = I_{{{iteratie}}} \Rightarrow$ soluția optimă!**")
            break
            
        # Daca nu, continuam
        st.warning(rf"**④ $TO: \forall \delta_{{ij}} \ge 0 \Rightarrow NU \Rightarrow$ o altă iterație.** $\min(\delta_{{ij}} < 0) = \delta_{{{intrata[0]+1}{intrata[1]+1}}} = {fmt(min_delta)}$")
        
        # Pagina 9: Identificam POLIGONUL pt pivotare
        st.write(rf"**Circuit $\Rightarrow$ se completează în tabelul $T_{{{iteratie}}}$ celula $({intrata[0]+1}, {intrata[1]+1})$ cu valoarea $\theta$**")
        circuit = gaseste_ciclu(celule_baza + [intrata], intrata)
        
        # AM REZOLVAT PROBLEMA CU CULOAREA ROSIE! Acum sirul nu mai are $ in el, deci merge st.latex brici.
        sir_circuit = " \\rightarrow ".join([rf"({r+1},{c+1})^{{{'+' if i%2==0 else '-'}}}" for i, (r, c) in enumerate(circuit)])
        st.latex(r"\text{Traseu: } " + sir_circuit)
        
        # Cautam cat e Theta (cantitatea pe care o mutam pe circuit)
        celule_minus = circuit[1::2]                            # celulele cu semnul MINUS sunt pe indici impari in lista
        theta = min([X_baza[r, c] for (r, c) in celule_minus])  
        iesita = [cell for cell in celule_minus if X_baza[cell[0], cell[1]] == theta][0] # cine atinge prima zero, pica afara din baza
        
        st.latex(rf"\theta = \min \{{X_{{ij}}^{{-}}\}} = \min \{{ " + ", ".join([fmt(X_baza[r,c]) for (r,c) in celule_minus]) + rf" \}} = {fmt(theta)}")
        
        # Aflam noul cost direct din formula, fara a recalcula toata matricea
        cost_nou = cost_curent + min_delta * theta
        st.latex(rf"f_{{{iteratie+1}}} = f_{{{iteratie}}} + \delta_{{{intrata[0]+1}{intrata[1]+1}}} \cdot X_{{{intrata[0]+1}{intrata[1]+1}}} = {fmt(cost_curent)} + ({fmt(min_delta)}) \cdot {fmt(theta)} = {fmt(cost_nou)}")
        
        # Acum chiar mutam efectiv cantitatile din matricea X ca sa ne preparam pt iteratia urmatoare
        semn = 1
        for (r, c) in circuit:                                  
            X_baza[r, c] += semn * theta
            semn *= -1
            
        celule_baza.remove(iesita)                              # ii dam kick celulei iesite
        celule_baza.append(intrata)                             # adaugam membra noua in baza
        cost_curent = cost_nou                                  # actualizam variabila de cost
        
        st.markdown("---")
        iteratie += 1

    # --------------------------------------------------------- PASUL 4: INTERPRETARE FINALA ----------------
    # Pagina 11 din pdf: concluziile
    st.markdown("<h3 style='color: #ff007f; text-align: center;'>📦 SOLUȚIA FINALĂ 📦</h3>", unsafe_allow_html=True)
    
    afiseaza_tabel_final(X_baza, A_lucru, B_lucru, celule_baza)
    st.markdown(f"<h2 style='color: #ff007f; text-align: center;'>Cost Total Minim: {fmt(cost_curent)} u.m.</h2>", unsafe_allow_html=True)
    
    st.write("💡 **Interpretare Managerială (Plan de Transport):**")
    for j in range(n):
        surse = []
        for i in range(m):
            if X_baza[i, j] > 0:
                # AM REZOLVAT INDicii A_1, A_2. Acum i-am bagat in dolari LaTeX
                surse.append(f"$A_{{{i+1}}}$ cu {fmt(X_baza[i,j])} u.p.")
        if surse:
            st.write(f"🔹 Beneficiarul **$B_{{{j+1}}}$** (necesar {fmt(B_lucru[j])} u.p.) se aprovizionează de la: " + ", ".join(surse))

    st.success("Astfel încât cheltuielile totale de transport ale companiei să fie minime!")
