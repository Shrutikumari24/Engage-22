import streamlit as st
from PIL import Image
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore');

#Setting page configuration
st.set_page_config(page_title="Automotive Analysis",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

#Inserting an image for the web app
image= Image.open('logo.jpg')
st.image(image)
#Title & description of the web app
st.title('Automotive Industry')
st.markdown("""
            This app performs data analysis to take informed decisions
            * **Python Libraries:** Pandas, Seaborn, Matplotlib, Streamlit
            * **Data Set Source:** The provided dataset from acehacker website
                                (https://acehacker.com/microsoft/engage2022/#challenges)
            """)

#To cache the data
@st.cache
def data_analysis():
    #reading the csv file
    microsoft_data = pd.read_csv("cars_engage_2022.csv")
    microsoft_data = pd.DataFrame(microsoft_data)
    #dropping the 1st unnamed column
    microsoft_data = microsoft_data.drop(microsoft_data.iloc[:,[0]], axis=1)
    #checking total null values in the data
    print(microsoft_data.isnull().sum())

    #dropping those columns which do not have 50% of data
    threshold = len(microsoft_data)*0.5
    microsoft_data.dropna(thresh=threshold, axis=1, inplace=True)
    #dropping the rows which do not have Company name
    microsoft_data = microsoft_data.dropna(subset=['Make'])

    #adding an extra column named Car
    microsoft_data['Car']=microsoft_data['Make']+' '+microsoft_data['Model']
    car = microsoft_data['Car']
    microsoft_data = microsoft_data.drop(columns=['Car'])
    microsoft_data.insert(loc=2, column='Car', value=car)
    
    #cleaning data
    microsoft_data['Ex-Showroom_Price'] = microsoft_data['Ex-Showroom_Price'].str.replace('Rs. ','').str.replace(',','').astype(float)
    microsoft_data['Height'] = microsoft_data['Height'].str.replace(' mm','',regex=False).astype(float)
    microsoft_data['Length'] = microsoft_data['Length'].str.replace(' mm','',regex=False).astype(float)
    microsoft_data['Width'] = microsoft_data['Width'].str.replace(' mm','',regex=False).astype(float)
    microsoft_data['Wheelbase'] = microsoft_data['Wheelbase'].str.replace(' mm','',regex=False).astype(float)
    microsoft_data['Fuel_Tank_Capacity'] = microsoft_data['Fuel_Tank_Capacity'].str.replace(' litres','',regex=False).astype(float)
    microsoft_data['Displacement'] = microsoft_data['Displacement'].str.replace(' cc','',regex=False).astype(float)
    microsoft_data.loc[microsoft_data.ARAI_Certified_Mileage == '9.8-10.0 km/litre','ARAI_Certified_Mileage'] = '10'
    microsoft_data.loc[microsoft_data.ARAI_Certified_Mileage == '10kmpl km/litre','ARAI_Certified_Mileage'] = '10'
    microsoft_data.loc[microsoft_data.ARAI_Certified_Mileage == '22.4-21.9 km/litre','ARAI_Certified_Mileage'] = '22.4'
    microsoft_data['ARAI_Certified_Mileage'] = microsoft_data['ARAI_Certified_Mileage'].str.replace(' km/litre','',regex=False).astype(float)
    microsoft_data['Basic_Warranty'] = microsoft_data['Basic_Warranty'].str.replace('(years/distance whichever comes first)','').str.replace('(Whichever comes earlier)','').str.replace('(whichever is earlier)','').str.replace('(whichever comes first)','')
    microsoft_data['Basic_Warranty']=microsoft_data['Basic_Warranty'].str.replace('(','').str.replace(')','')
    microsoft_data.rename(columns = {'Ex-Showroom_Price':'Ex-Showroom_Price (in Rs.)', 'Height':'Height (in mm)', 'Length':'Length (in mm)', 'Width':'Width (in mm)', 'Wheelbase':'Wheelbase (in mm)', 'Fuel_Tank_Capacity':'Fuel_Tank_Capacity (in mL)', 'Displacement':'Displacement (in cc)', 'ARAI_Certified_Mileage':'ARAI_Certified_Mileage (in km/L)'}, inplace = True)
    
    #making a copy of the data and storing it in df
    df=microsoft_data.copy()
    df.columns = [ (i + 1) for i in range(len(df.columns)) ]
    #storing all the object datatype columns in df_obj
    df_obj=df.select_dtypes(include = 'object')
    
    #fiiling all null values of object datatype column with mode
    for i in df_obj:
        df[i].fillna(df[i].mode()[0], inplace=True)
        microsoft_data.iloc[:,i-1].fillna(microsoft_data.iloc[:,i-1].mode()[0], inplace=True)

    #storing all the float datatype columns in df_obj
    df_ft=df.select_dtypes(include = 'float64')

    #fiiling all null values of float datatype column with mean
    for i in df_ft:
        df[i].fillna(df[i].mean(), inplace=True)
        microsoft_data.iloc[:,i-1].fillna(microsoft_data.iloc[:,i-1].mode()[0], inplace=True)
        
        microsoft_data.info()
        print(microsoft_data.head())
        print(microsoft_data.describe())
        return microsoft_data

microsoft_data=data_analysis()

st.write('**Size** of the data set after cleaning and filling missing values: ',  microsoft_data.shape)

#working with stremlit
#slecting company
st.sidebar.header('Select the Company')
company= microsoft_data.groupby('Make')
sorted_company=sorted(microsoft_data['Make'].unique())
select_company=st.sidebar.selectbox('Company', sorted_company)
df_selected_company=microsoft_data[(microsoft_data['Make'] == select_company)]

#selecting different models
st.sidebar.header('Select the Model')
sorted_model = sorted(df_selected_company['Model'].unique())
select_model=st.sidebar.multiselect('Model', sorted_model)
df_selected_model=df_selected_company[(df_selected_company['Model'].isin(select_model))]

#Displaying of selected data
st.header('Display the Selected Company Data')
st.write('Data Dimenions: '+ str(df_selected_model.shape[0]) + ' rows ' + str(df_selected_model.shape[1]) +' columns')
st.dataframe(df_selected_model)

st.markdown('##')
sel_col, disp_col=st.columns((1,2))

#listing important features
dF_selected_feature=df_selected_model.copy()
c=['Ex-Showroom_Price (in Rs.)', 'Displacement (in cc)', 'Cylinders', 'Drivetrain', 'Fuel_Tank_Capacity (in mL)', 'Fuel_Type',  'Height (in mm)', 'Length (in mm)', 'Width (in mm)', 'Body_Type', 'Doors', 'ARAI_Certified_Mileage (in km/L)', 'Gears', 'Power', 'Torque', 'Seating_Capacity', 'Type', 'Wheelbase (in mm)', 'Number_of_Airbags']
df_selected_feature = dF_selected_feature[c]
sel_col.subheader('List of Features')
sel_col.write(df_selected_feature.columns)
input_feature=disp_col.text_input('Type the Feature to see the distribution graph')

df_ft1=df_selected_feature.select_dtypes(include = 'float64')
df_obj1=df_selected_feature.select_dtypes(include = 'object')

#plotting distribution graphs for analysis
if input_feature=='ARAI_Certified_Mileage (in km/L)':
    col1, col2=st.columns((1,1))
    fig,ax = plt.subplots()
    sns.histplot(data=df_selected_model, x=input_feature, bins=20, alpha=0.6, color='#f54242')
    ax1 = ax.twinx()
    sns.kdeplot(data=df_selected_model, x=input_feature, alpha=0.2,fill= True,color="#fc4e4e",linewidth=0)
    ax1.grid()
    ax.set_title('Histogram of '+ input_feature + ' data',fontsize=10)
    ax.set_xlabel(input_feature)
    col1.pyplot(fig)
    fig1, ax2= plt.subplots()
    sns.scatterplot(data=df_selected_model, x=input_feature, y='Power',hue='Model');
    ax2.set_title('Relation Between Mileage and Power of Cars')
    ax2.set_xlabel('Mileage')
    ax2.set_ylabel('Power')
    col2.pyplot(fig1)

elif input_feature in df_ft1.columns:
    fig,ax = plt.subplots()
    sns.histplot(data=df_selected_model, x=input_feature,bins=20, alpha=0.6, color='#f54242')
    ax1 = ax.twinx()
    sns.kdeplot(data=df_selected_model, x=input_feature, alpha=0.2,fill= True,color="#fc4e4e", linewidth=0)
    ax1.grid()
    ax.set_title('Histogram of '+ input_feature + ' data',fontsize=10)
    ax1.set_xlabel(input_feature)
    st.pyplot(fig)
elif input_feature in df_obj1.columns:
    col1, col2=st.columns((1,1))
    fig, ax = plt.subplots()
    sns.countplot(data=df_selected_model, y=input_feature, alpha=0.6, color='#f54242')
    ax.set_title('Number of ' + input_feature + ' frequency diagram', fontsize=10)
    ax.set_xlabel('Count')
    ax.set_ylabel(input_feature);
    col1.pyplot(fig)
    fig1, ax1= plt.subplots()
    sns.scatterplot(data=df_selected_model, y=input_feature, x='Ex-Showroom_Price (in Rs.)',hue='Model');
    ax1.set_title('Relation Between ' + input_feature + ' and Ex-Showroom Price of Cars')
    ax1.set_ylabel(input_feature)
    ax1.set_xlabel('Ex-Showroom Price')
    col2.pyplot(fig1)
    st.write('**Zoom-in** to view the graphs clearly')

st.markdown('##')
st.write('For more Frequenty Asked Questions **CLICK** \'**_Yes_**\':')
check = st.checkbox('Yes')
if check:
    nested_btn=st.button('Which Fuel Type is used in most of the Automobiles?')
    if nested_btn:
        fig,ax = plt.subplots()
        sns.histplot(data=microsoft_data, x='Fuel_Type',bins=5, alpha=0.6, color='#f54242')
        ax.set_title('Histogram of Fuel Type data')
        ax.set_xlabel('Fuel Type')
        st.pyplot(fig)
        st.write('* **600** Automobiles use petrol as their Fuel Type, and as we know, there are 1201 cars in the data. As a result, nearly **half** of all cars run on **_Petrol_**.')
        st.write('The second most used Fuel Type is **Diesel**. Therefore, it can be deduced that most cars run on either **_Gas_** or **_Diesel_**.')
    nested_btn_1 = st.button('Show the range of Ex-Showroom Price')
    if nested_btn_1:
        fig,ax = plt.subplots()
        sns.histplot(data=microsoft_data, x='Ex-Showroom_Price (in Rs.)',bins=15, alpha=0.6, color='#f54242')
        ax.set_title('Histogram of Ex-Showroom Price data')
        ax.set_xlabel('Ex-Showroom Price')
        st.pyplot(fig)
        st.write('* According to the graph, the maximum car price ranges from **10 lakh** to **16 lakh**.')
    nested_btn_2 = st.button('* Number of Doors in most of the Automobiles')
    if nested_btn_2:
        fig,ax = plt.subplots()
        sns.histplot(data=microsoft_data, x='Doors',bins=20, alpha=0.6, color='#f54242')
        ax.set_title('Histogram of Number of Doors data')
        ax.set_xlabel('Number of Doors')
        st.pyplot(fig)
        st.write('* **800** Automobiles has **five** doors, and as we know, there are 1201 cars in the data. As a result, nearly 67% of all cars has **_Five Doors_**.')
    nested_btn_3 = st.button('Which Car Body Type is most popular?')
    if nested_btn_3:
        fig,ax = plt.subplots()
        sns.countplot(data=microsoft_data, y='Body_Type', alpha=0.6, color='#f54242')
        ax.set_title('Frequency of Car Body Type data')
        ax.set_ylabel('Body Type')
        st.pyplot(fig)
        st.write('* **SUVs** are the most common car body type, followed by **Hatchbacks** and **Sedans**.')
    nested_btn_4 = st.button('Which Company produces maximum number of cars?')
    if nested_btn_4:
        df1 = microsoft_data[(microsoft_data['Make'].isin(['Honda', 'Hyundai', 'Mahindra', 'Maruti Suzuki', 'Tata', 'Toyota']))]
        fig,ax = plt.subplots()
        sns.countplot(data=df1, y='Make', color='#f54242')
        ax.set_title('Frequency of Companies data')
        ax.set_ylabel('Comapny')
        st.pyplot(fig)
        st.write('* **Maruti Suzuki** manufactures the most cars, followed by **Hyundai**, **Mahindra** and **Tata**.')
    nested_btn_6=st.button('Relation between Company and Car Ex-Showroom Price')
    if nested_btn_6:
        df3 = microsoft_data[(microsoft_data['Make'].isin(['Audi', 'Aston Martin', 'Bentley', 'BMW', 'Bulgatti', 'Ferrari', 'Jaguar', 'Lamborghini', 'Land Rover Rover', 'Lexus', 'Maserati', 'Porsche', 'Volvo']))]
        fig,ax = plt.subplots()
        sns.boxplot(data=df3, y='Make', x='Ex-Showroom_Price (in Rs.)');
        ax.set_title('')
        ax.set_ylabel('Company')
        ax.set_xlabel('Ex-Showroom Price')
        st.pyplot(fig)
        st.write('* According to the graph, **Lamborghini, Bentley, and Ferrai** produce the most expensive cars, with prices exceeding **3 crore**.')
    nested_btn_7=st.button('What is the Basic Warranty applied to Automobiles?')
    if nested_btn_7:
        fig,ax = plt.subplots()
        sns.countplot(data=microsoft_data, y='Basic_Warranty', alpha=0.6, color='#f54242')
        ax.set_title('Frequency of Warranty data')
        ax.set_ylabel('Warranty')
        st.pyplot(fig)
        st.write('* According to the graph, **2 Years/Unlimited Kms** is the most common Basic Warranty provided by the Companies')

st.markdown('##')
col3, col4=st.columns([2.2,1])
col4.markdown("""
            * **Name:** Shruti Kumari
            * **Email:** skumari242000@gmail.com
            """)
