import streamlit as st
import pdfplumber
import pandas as pd
import io

# Titre et description de l'application
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

# Fonction pour extraire les transactions du fichier PDF
def extract_data_from_pdf(pdf_file):
    transactions = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            for line in lines:
                # Vérification pour s'assurer que la ligne contient une date et un montant
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
                        st.warning(f"Impossible de convertir le montant : {montant_str}")
                        
    return transactions

# Fonction pour convertir le DataFrame en fichier Excel
@st.cache_data
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# Interface pour télécharger le fichier PDF
uploaded_pdf = st.file_uploader("Téléchargez le fichier PDF du relevé de carte de crédit", type="pdf")

if uploaded_pdf is not None:
    # Extraire les données du fichier PDF
    data = extract_data_from_pdf(uploaded_pdf)

    if data:
        # Convertir les données en DataFrame
        df = pd.DataFrame(data)
        
        # Afficher un aperçu des données dans Streamlit
        st.write("Aperçu des données :")
        st.dataframe(df)

        # Convertir le DataFrame en Excel et proposer le téléchargement
        excel_data = convert_df_to_excel(df)
        st.download_button(
            label="Télécharger le fichier Excel",
            data=excel_data,
            file_name="transactions_carte_credit.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.error("Aucune transaction valide n'a été trouvée dans le fichier PDF.")
