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
    
    /* animatie pentru fundite baby pink care cad de sus */
    @keyframes fallDown {
        0% { top: -100px; transform: rotate(0deg); opacity: 1; }
        100% { top: 100vh; transform: rotate(360deg); opacity: 0; }
    }
    .bow {
        position: fixed; 
        z-index: 99999; 
        pointer-events: none; 
        user-select: none; 
        animation-name: fallDown; 
        animation-timing-function: linear; 
        animation-iteration-count: 1; 
        animation-fill-mode: forwards;
        color: #fddde6; 
        text-shadow: 0px 0px 4px #ff007f, 0px 0px 8px #ff007f;
    }
    </style>
""", unsafe_allow_html=True)                                    # design css pt titlu si fundite

def afiseaza_fundite_baby_pink():                               # functie care genereaza 50 de fundite zburatoare
    bows_html = "<div style='position: fixed; top: 0; left: 0; width: 0px; height: 0px; pointer-events: none; z-index: 99999; overflow: visible;'>"
    for _ in range(50):
        left = random.randint(0, 100)
        duration = random.uniform(3.0, 6.0)
        delay = random.uniform(0, 1.5)
        size = random.uniform(1.5, 3.5)
        bows_html += f"<div class='bow' style='left: {left}vw; animation-duration: {duration}s; animation-delay: {delay}s; font-size: {size}rem;'>🎀</div>"
    bows_html += "</div>"
    st.markdown(bows_html, unsafe_allow_html=True)

def fmt(val):                                                   # functie STILIZATA pt a scapa de erorile de np.float64 din LaTeX!!
    if pd.isna(val) or val is None: return ""
    if isinstance(val, (np.floating, float)):
        return str(int(val)) if val.is_integer() else f"{val:.2f}"
    return str(val)

def afiseaza_tabel_x(X, m, n, baza=None):                       # functie generica pt a afisa tabelul X la orice pas
    df = pd.DataFrame(X, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    df = df.astype(object)
    for col in df.columns:
        df[col] = df[col].apply(lambda x: int(x) if pd.notna(x) and str(x).replace('.','',1).isdigit() and float(x).is_integer() else x)
        
    def coloreaza_baza(data):
        stiler = pd.DataFrame('', index=data.index, columns=data.columns)
        if baza is not None:
            for (i, j) in baza:
                stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;'
        return stiler
    st.dataframe(df.style.apply(coloreaza_baza, axis=None))

def afiseaza_tabel_final(X, A, B, baza=None):                   # afiseaza tabelul final curat
    m, n = len(A), len(B)
    df = pd.DataFrame(X, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
    df['Disp. (a_i)'] = [fmt(x) for x in A]                                  
    df.loc['Necesar (b_j)'] = [fmt(x) for x in B] + [fmt(sum(A))]                
    
    def coloreaza_mixt(data):                                   # functia de design finala
        stiler = pd.DataFrame('', index=data.index, columns=data.columns)
        if baza is not None:
            for (i, j) in baza:
                stiler.iloc[i, j] = 'background-color: #fddde6; font-weight: bold; color: #ff007f;'
        stiler.iloc[-1, :] = 'background-color: #d4edda; font-weight: bold; color: #155724; border-top: 2px solid #28a745;'
        stiler.iloc[:, -1] = 'background-color: #d4edda; font-weight: bold; color: #155724; border-left: 2px solid #28a745;'
        stiler.iloc[-1, -1] = 'background-color: #28a745; color: white; font-weight: bold;'
        return stiler
    st.dataframe(df.style.apply(coloreaza_mixt, axis=None), use_container_width=True)

                                                                # ALGORITMI PROBLEMA TRANSPORTURILOR

def echilibreaza_problema(C, A, B):                             # pas 1: verificam conditia de echilibru
    sum_A, sum_B = sum(A), sum(B)
    C_echil, A_echil, B_echil = np.array(C, dtype=float), list(A), list(B)
    
    if sum_A > sum_B:                                           # cerere < oferta -> bagam beneficiar fictiv
        B_echil.append(sum_A - sum_B)
        C_echil = np.hstack((C_echil, np.zeros((C_echil.shape[0], 1))))
        return C_echil, A_echil, B_echil, "Beneficiar Fictiv B*"
    elif sum_B > sum_A:                                         # oferta < cerere -> bagam furnizor fictiv
        A_echil.append(sum_B - sum_A)
        C_echil = np.vstack((C_echil, np.zeros((1, C_echil.shape[1]))))
        return C_echil, A_echil, B_echil, "Furnizor Fictiv A*"
    return C_echil, A_echil, B_echil, "Echilibrată"

def coltul_nv(A, B):                                            # pas 2: calculam prima baza prin metoda Coltului N-V
    m, n = len(A), len(B)
    X = np.zeros((m, n))
    baza, a_temp, b_temp = [], list(A), list(B)
    i, j = 0, 0
    
    while i < m and j < n:
        minim = min(a_temp[i], b_temp[j])
        X[i, j] = minim
        baza.append((i, j))
        a_temp[i] -= minim
        b_temp[j] -= minim
        
        if a_temp[i] == 0 and b_temp[j] == 0:                   # solutie pt degenerare direct din algoritm
            if j < n - 1: j += 1
            elif i < m - 1: i += 1
            else: break
        elif a_temp[i] == 0: i += 1
        else: j += 1
    return X, baza

def calculeaza_potentiale(C, baza, m, n):                       # metoda potentialelor ui + vj = cij
    u, v = [None] * m, [None] * n
    u[0] = 0                                                    # fixam u1=0 (sistem compatibil nedeterminat)
    
    schimbare = True                                            
    while (None in u or None in v) and schimbare:
        schimbare = False
        for (i, j) in baza:
            if u[i] is not None and v[j] is None: 
                v[j] = C[i, j] - u[i]
                schimbare = True
            elif v[j] is not None and u[i] is None: 
                u[i] = C[i, j] - v[j]
                schimbare = True
                
    for i in range(m):
        if u[i] is None: u[i] = 0
    for j in range(n):
        if v[j] is None: v[j] = 0
    return u, v

def calculeaza_delta(C, u, v, m, n):                            # calculam costurile modificate (C tilde) si ecarturile (Delta)
    Delta, C_tilde = np.zeros((m, n)), np.zeros((m, n))
    for i in range(m):
        for j in range(n):
            C_tilde[i, j] = u[i] + v[j]                         
            Delta[i, j] = C[i, j] - C_tilde[i, j]               
    return C_tilde, Delta

def gaseste_ciclu(celule_baza, start):                          # cautam traseul (+, -, +, -) ca in seminar
    def cauta_drum(nod_curent, drum, e_orizontal):
        for urmator in celule_baza:
            if urmator != nod_curent:
                if e_orizontal and urmator[0] == nod_curent[0]: 
                    if urmator == start and len(drum) >= 4: return drum
                    if urmator not in drum:
                        rez = cauta_drum(urmator, drum + [urmator], False)
                        if rez: return rez
                elif not e_orizontal and urmator[1] == nod_curent[1]: 
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

st.markdown("<h3 style='color: #ff007f;'>📝 Datele Problemei</h3>", unsafe_allow_html=True)

# TABEL COMBINAT DE INPUT
cols = [f"B{j+1}" for j in range(n_dest)] + ["Oferta (a_i)"]
rows = [f"A{i+1}" for i in range(m_surse)] + ["Cerere (b_j)"]

df_input_initial = pd.DataFrame(index=rows, columns=cols)       

# Datele default initiale fix din Ex 1
C_curs = [[1, 3, 2, 4], [3, 1, 2, 2], [2, 3, 2, 1]]
A_curs = [30, 39, 21]
B_curs = [25, 20, 30, 15]

for i in range(m_surse):                                        
    for j in range(n_dest):
        if m_surse == 3 and n_dest == 4: df_input_initial.iloc[i, j] = C_curs[i][j]
        else: df_input_initial.iloc[i, j] = random.randint(1, 9)
            
    if m_surse == 3 and n_dest == 4: df_input_initial.iloc[i, -1] = A_curs[i]
    else: df_input_initial.iloc[i, -1] = 20
    
for j in range(n_dest):
    if m_surse == 3 and n_dest == 4: df_input_initial.iloc[-1, j] = B_curs[j]
    else: df_input_initial.iloc[-1, j] = 15
        
df_input_initial.iloc[-1, -1] = None                            

def coloreaza_input(data):                                      # Delimitam Oferta/Cererea vizual
    stiler = pd.DataFrame('', index=data.index, columns=data.columns)
    stiler.iloc[-1, :] = 'background-color: #f0f2f6; font-weight: bold; border-top: 2px solid #555;'
    stiler.iloc[:, -1] = 'background-color: #f0f2f6; font-weight: bold; border-left: 2px solid #555;'
    stiler.iloc[-1, -1] = 'background-color: #e0e4eb;'          
    return stiler

st.write("**Introduceți Costurile Unitare ($C_{ij}$), Oferta și Cererea:**")
edited_df = st.data_editor(df_input_initial.style.apply(coloreaza_input, axis=None), use_container_width=True) 

C_input = edited_df.iloc[:-1, :-1].values.astype(float)         
A_input = edited_df.iloc[:-1, -1].values.astype(float).tolist() 
B_input = edited_df.iloc[-1, :-1].values.astype(float).tolist() 

if st.button("🚀 Rezolvă Problema Pas cu Pas", type="primary", use_container_width=True):
    
    afiseaza_fundite_baby_pink()                                # <3
    st.divider()
    
                                                                # PAS 1: ECHILIBRUL (Pagina 1-2 din Seminar)
    st.markdown("<h3 style='color: #ff007f;'>Pasul 1. Verificăm dacă avem PTE</h3>", unsafe_allow_html=True)
    C_lucru, A_lucru, B_lucru, status = echilibreaza_problema(C_input, A_input, B_input)
    
    sum_A, sum_B = sum(A_input), sum(B_input)
    st.latex(rf"\Sigma D = {fmt(sum_A)} \quad ; \quad \Sigma N = {fmt(sum_B)}")
    
    if status == "Echilibrată": 
        st.latex(r"\Sigma D = \Sigma N \Rightarrow \text{avem PTE}")
    else: 
        st.warning(f"⚠️ $\Sigma D \neq \Sigma N$. Se introduce un **{status}** cu costuri de transport $C_{{ij}} = 0$.")
    
    m, n = len(A_lucru), len(B_lucru)

                                                                # PAS 2: SOLUTIA INITIALA (Pagina 3-4 din Seminar)
    st.markdown("<h3 style='color: #ff007f;'>Pasul 2. Metoda Colțului N-V</h3>", unsafe_allow_html=True)
    st.write("Aplicăm metoda Colțului N-V și completăm tabelul $T_0$:")
    
    X_baza, celule_baza = coltul_nv(A_lucru, B_lucru)
    afiseaza_tabel_x(X_baza, m, n, celule_baza)
    
    v_max, v_curent = m + n - 1, len(celule_baza)               
    st.latex(rf"V = m + n - 1 = {m} + {n} - 1 = {v_max}")
    st.latex(rf"NC = \text{{nr. celule completate in }} T_0 = {v_curent}")
    
    if v_curent == v_max: 
        st.success(r"$NC = V \Rightarrow$ soluție **nedegenerată**. Continuăm rezolvarea.")
    else: 
        st.error(r"$NC < V \Rightarrow$ soluție **degenerată**. S-au adăugat alocări de 0 pentru perturbare ($\epsilon$).")

    # Calculul costului f0 (Pagina 6 din Seminar)
    cost_curent = np.sum(X_baza * C_lucru)
    formule_f0 = [f"{fmt(C_lucru[i,j])} \cdot {fmt(X_baza[i,j])}" for (i,j) in celule_baza]
    st.latex(r"f_0 = f_{min}(X^0) = \sum c_{ij} \cdot X_{ij} = " + " + ".join(formule_f0) + f" = {fmt(cost_curent)}")

                                                                # PAS 3: ALGORITMUL MODI (Pagina 6-10 din Seminar)
    st.divider()
    st.markdown("<h3 style='color: #ff007f;'>Pasul 3. Aplicăm TO (Testul de Optimalitate)</h3>", unsafe_allow_html=True)
    
    iteratie, max_iter = 0, 15                                  
    
    while iteratie < max_iter:
        st.markdown(f"<h4 style='color: #333;'>Iterația $I_{iteratie} (T_{iteratie}, X_{iteratie}, f_{iteratie})$</h4>", unsafe_allow_html=True)
        
        # Pagina 6: Sistemul S
        u, v = calculeaza_potentiale(C_lucru, celule_baza, m, n)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("① Sistemul $S: u_i + v_j = c_{ij}$")
            sistem_latex = r"\begin{cases} "
            for (i, j) in celule_baza:
                sistem_latex += rf"u_{i+1} + v_{j+1} = {fmt(C_lucru[i,j])} \\ "
            sistem_latex += r"\end{cases}"
            st.latex(sistem_latex)
        
        with col2:
            st.write(rf"Alegem $u_1 = 0 \Rightarrow$")
            rez_latex = r"\begin{cases} "
            for i in range(m): rez_latex += rf"u_{i+1} = {fmt(u[i])} \\ "
            for j in range(n): rez_latex += rf"v_{j+1} = {fmt(v[j])} \\ "
            rez_latex += r"\end{cases}"
            st.latex(rez_latex)

        # Pagina 7-8: Tabelele C tilde si Delta
        C_tilde, Delta = calculeaza_delta(C_lucru, u, v, m, n)
        
        col3, col4 = st.columns(2)
        with col3:
            st.write("② Tabel $\tilde{C} \Rightarrow \tilde{C}_{ij} = u_i + v_j$")
            df_ctilde = pd.DataFrame(C_tilde, index=[f"{fmt(u[i])}=u{i+1}" for i in range(m)], columns=[f"v{j+1}={fmt(v[j])}" for j in range(n)])
            st.dataframe(df_ctilde.astype(object).applymap(fmt))
            
        with col4:
            st.write("③ Tabel $\Delta \Rightarrow \delta_{ij} = C_{ij} - \tilde{C}_{ij}$")
            df_delta = pd.DataFrame(Delta, index=[f"A{i+1}" for i in range(m)], columns=[f"B{j+1}" for j in range(n)])
            
            # Highlight celulele cu cost indirect negativ
            def style_delta(val):
                if val < 0: return 'background-color: #ffcccc; color: red; font-weight: bold;'
                return ''
            st.dataframe(df_delta.style.applymap(style_delta))

        # Pagina 8: Decizia STOP sau Continuam
        este_optim, min_delta, intrata = True, 0, None
        for i in range(m):
            for j in range(n):
                if (i, j) not in celule_baza and Delta[i, j] < min_delta: 
                    min_delta = Delta[i, j]
                    intrata = (i, j)
                    este_optim = False
                    
        if este_optim:
            st.success(r"④ $TO: \forall \delta_{ij} \ge 0 \Rightarrow DA \Rightarrow STOP \Rightarrow I_{STOP} = I_{" + str(iteratie) + r"} \Rightarrow$ soluția optimă!")
            break
            
        st.warning(rf"④ $TO: \forall \delta_{ij} \ge 0 \Rightarrow NU \Rightarrow$ o altă iterație. $\min(\delta_{{ij}} < 0) = \delta_{{{intrata[0]+1}{intrata[1]+1}}} = {fmt(min_delta)}$")
        
        # Pagina 9: Circuitul
        st.write(rf"**Circuit $\Rightarrow$ se completează în tabelul $T_{iteratie}$ celula $({intrata[0]+1}, {intrata[1]+1})$ cu valoarea $\theta$**")
        circuit = gaseste_ciclu(celule_baza + [intrata], intrata)
        
        sir_circuit = " $\\rightarrow$ ".join([rf"({r+1},{c+1})^{{{'+' if i%2==0 else '-'}}}" for i, (r, c) in enumerate(circuit)])
        st.latex(r"\text{Traseu: } " + sir_circuit)
        
        celule_minus = circuit[1::2]
        theta = min([X_baza[r, c] for (r, c) in celule_minus])  
        iesita = [cell for cell in celule_minus if X_baza[cell[0], cell[1]] == theta][0]
        
        st.latex(rf"\theta = \min \{{X_{{ij}}^{{-}}\}} = \min \{{ " + ", ".join([fmt(X_baza[r,c]) for (r,c) in celule_minus]) + rf" \}} = {fmt(theta)}")
        
        # Pagina 10: Calcul Cost Nou
        cost_nou = cost_curent + min_delta * theta
        st.latex(rf"f_{{{iteratie+1}}} = f_{{{iteratie}}} + \delta_{{{intrata[0]+1}{intrata[1]+1}}} \cdot X_{{{intrata[0]+1}{intrata[1]+1}}} = {fmt(cost_curent)} + ({fmt(min_delta)}) \cdot {fmt(theta)} = {fmt(cost_nou)}")
        
        # Actualizam matricea in spate pentru pasul urmator
        semn = 1
        for (r, c) in circuit:                                  
            X_baza[r, c] += semn * theta
            semn *= -1
            
        celule_baza.remove(iesita)                              
        celule_baza.append(intrata)                             
        cost_curent = cost_nou                  
        
        st.markdown("---")
        iteratie += 1

                                                                # PAS 4: INTERPRETARE FINALA (Pagina 11 din Seminar)
    st.markdown("<h3 style='color: #ff007f; text-align: center;'>📦 SOLUȚIA FINALĂ 📦</h3>", unsafe_allow_html=True)
    
    afiseaza_tabel_final(X_baza, A_lucru, B_lucru, celule_baza)
    st.markdown(f"<h2 style='color: #ff007f; text-align: center;'>Cost Total Minim: {fmt(cost_curent)} u.m.</h2>", unsafe_allow_html=True)
    
    # Interpretare textuala simpatica si utila
    st.write("💡 **Interpretare Managerială (Plan de Transport):**")
    for j in range(n):
        surse = []
        for i in range(m):
            if X_baza[i, j] > 0:
                surse.append(f"A_{i+1} cu {fmt(X_baza[i,j])} u.p.")
        if surse:
            st.write(f"🔹 Beneficiarul **$B_{j+1}$** (necesar {fmt(B_lucru[j])} u.p.) se aprovizionează de la: " + ", ".join(surse))

    st.success("Astfel încât cheltuielile totale de transport ale companiei să fie minime!")
