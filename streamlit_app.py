import streamlit as st
import pdfplumber
import pandas as pd
import io
import re

# Fonction pour vérifier si une chaîne correspond au format d'une date (par exemple, JJ-MM-AAAA)
def is_valid_date(date_str):
    return bool(re.match(r"\d{2}-\d{2}-\d{4}", date_str))

# Fonction pour extraire les transactions du fichier PDF
def extract_data_from_pdf(pdf_file):
    transactions = []
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    montant_pattern = r"-?\d+,\d{2}"

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    # Vérifier si la ligne contient un montant
                    if re.search(montant_pattern, line):
                        # Extraire toutes les dates dans la ligne
                        dates_in_line = re.findall(date_pattern, line)
                        if dates_in_line:
                            date = dates_in_line[0]  # Première date comme date de transaction
                        else:
                            continue  # Ignorer si aucune date n'est trouvée

                        # Vérifier si la date extraite est valide
                        if not is_valid_date(date):
                            continue

                        # Extraire le montant
                        montant_match = re.search(montant_pattern, line)
                        if montant_match:
                            montant_str = montant_match.group()
                            montant = float(montant_str.replace(",", "."))
                        else:
                            continue  # Ignorer si aucun montant n'est trouvé

                        # Supprimer toutes les dates de la ligne pour obtenir le libellé
                        line_without_dates = re.sub(date_pattern, '', line)
                        # Supprimer le montant du libellé
                        line_without_montant = re.sub(montant_pattern, '', line_without_dates)
                        libelle = line_without_montant.strip()

                        # Supprimer les espaces multiples et les caractères spéciaux
                        libelle = re.sub(' +', ' ', libelle)
                        libelle = libelle.strip("-•: ")

                        # Ajouter la transaction à la liste
                        transactions.append({"Date": date, "Libelé": libelle, "Montant": montant})
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
st.title("💳 StatementXtract")
st.write("""
Bienvenue sur **StatementXtract**, l'application qui simplifie la conversion de vos relevés de carte de crédit PDF en fichiers Excel pour les importer dans Odoo.

### Fonctionnalités :
- Importez votre relevé de carte de crédit au format PDF.
- StatementXtract extrait automatiquement les informations de date, libellé et montant pour chaque transaction.
- Téléchargez le fichier Excel généré.
- Importez le fichier Excel dans le journal de la carte de crédit dans Odoo pour une gestion simplifiée de vos dépenses.

**Conseil :** Assurez-vous que le fichier PDF suit un format standard pour une extraction optimale des données.

Commencez dès maintenant en téléchargeant votre fichier PDF !
""")

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

        # Calculer et afficher le total des dépenses
        total_depenses = df['Montant'].sum()
        st.write(f"**Total des dépenses :** {total_depenses:.2f} EUR")

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
