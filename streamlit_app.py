import streamlit as st

st.title("🎈 StatementXtract")
st.write("""
# StatementXtract
Bienvenue sur **StatementXtract**, l'application qui simplifie la conversion de vos relevés de carte de crédit PDF en fichiers Excel.

### Fonctionnalités :
- Importez votre relevé de carte de crédit au format PDF.
- StatementXtract extrait automatiquement les informations de date, libellé et montant pour chaque transaction.
- Téléchargez le fichier Excel généré pour une gestion simplifiée de vos dépenses.

**Conseil :** Assurez-vous que le fichier PDF suit un format standard pour une extraction optimale des données.

Commencez dès maintenant en téléchargeant votre fichier PDF !
""")

import streamlit as st
import pdfplumber
import pandas as pd

def extract_data_from_pdf(pdf_file):
    transactions = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            for line in lines:
                # Vérification de base pour s'assurer que la ligne contient une date et un montant
                if any(char.isdigit() for char in line) and 'EUR' in line:
                    parts = line.split()
                    date = parts[0]
                    libelle = " ".join(parts[1:-1])
                    montant_str = parts[-1].replace("EUR", "").strip()
                    
                    # Bloc try-except pour gérer les erreurs de conversion
                    try:
                        montant = float(montant_str.replace(",", "."))
                        transactions.append({"Date": date, "Libelé": libelle, "Montant": montant})
                    except ValueError:
                        # Affiche un message d'erreur pour le montant non convertible
                        print(f"Impossible de convertir le montant : {montant_str}")
                        
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
