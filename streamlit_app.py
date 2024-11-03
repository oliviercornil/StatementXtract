import streamlit as st
import pdfplumber
import pandas as pd
import io

# Fonction pour extraire les transactions d'un fichier PDF
def extract_data_from_pdf(pdf_file):
    transactions = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            for line in lines:
                # Vérifie si la ligne contient une date et un montant (adapté selon la structure des fichiers PDF)
                if any(char.isdigit() for char in line) and ('EUR' in line or '-' in line):
                    parts = line.split()
                    try:
                        date = parts[0]  # Extraire la date
                        libelle = " ".join(parts[1:-1])  # Extraire le libellé
                        montant_str = parts[-1].replace("EUR", "").strip()
                        montant = float(montant_str.replace(",", "."))
                        transactions.append({"Date": date, "Libelé": libelle, "Montant": montant})
                    except ValueError:
                        # Ignorer les lignes qui ne correspondent pas au format attendu
                        continue
    return transactions

# Fonction pour convertir les données en fichier Excel
@st.cache_data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Interface de l'application
st.title("Extraction de Dépenses de Carte de Crédit en Excel")
uploaded_pdf = st.file_uploader("Téléchargez le fichier PDF de dépenses de carte de crédit", type="pdf")

if uploaded_pdf is not None:
    # Extraire les données du PDF
    data = extract_data_from_pdf(uploaded_pdf)

    if data:
        # Convertir les données en DataFrame et filtrer les lignes indésirables
        df = pd.DataFrame(data)
        # Exclusion de certaines lignes non pertinentes
        df = df[~df['Libelé'].str.contains("Limited'utilisation|Soldeprécédent|DOMICILIATION|Décomptevia", case=False)]
        
        # Afficher les données
        st.write("Aperçu des données extraites :")
        st.dataframe(df)

        # Convertir en Excel et proposer le téléchargement
        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="Télécharger le fichier Excel",
            data=excel_data,
            file_name="transactions_carte_credit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Aucune transaction valide n'a été trouvée dans le fichier PDF.")
