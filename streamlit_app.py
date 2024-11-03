import streamlit as st

st.title("🎈 StatementXtract")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import pdfplumber
import pandas as pd

# Fonction pour extraire les données du PDF
def extract_data_from_pdf(pdf_file):
    transactions = []
    with pdfplumber.open(pdf_file) as pdf:
        # Parcourir les pages du PDF
        for page in pdf.pages:
            text = page.extract_text()
            # Rechercher les lignes contenant les transactions (ici, cela doit être adapté selon la structure du fichier PDF)
            lines = text.split("\n")
            for line in lines:
                # Exemple : vérifier si une ligne contient une date et un montant, cela peut nécessiter des ajustements
                if any(char.isdigit() for char in line) and 'EUR' in line:
                    parts = line.split()
                    date = parts[0]
                    libelle = " ".join(parts[1:-1])
                    montant = parts[-1].replace("EUR", "").strip()
                    transactions.append({"Date": date, "Libelé": libelle, "Montant": float(montant.replace(",", "."))})
    return transactions

# Interface Streamlit pour uploader le fichier PDF
st.title("Transformation du relevé de carte de crédit en fichier Excel")
uploaded_pdf = st.file_uploader("Téléchargez le fichier PDF du relevé de carte", type="pdf")

if uploaded_pdf is not None:
    # Extraire les données du fichier PDF
    data = extract_data_from_pdf(uploaded_pdf)

    if data:
        # Convertir les données en DataFrame
        df = pd.DataFrame(data)
        
        # Afficher un aperçu des données dans Streamlit
        st.write("Aperçu des données:")
        st.dataframe(df)

        # Téléchargement du fichier Excel
        @st.cache_data
        def convert_df_to_excel(df):
            # Convertir le DataFrame en fichier Excel
            return df.to_excel(index=False, encoding='utf-8')

        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="Télécharger le fichier Excel",
            data=excel_data,
            file_name="transactions_carte_credit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Aucune transaction n'a été trouvée dans le fichier PDF.")
