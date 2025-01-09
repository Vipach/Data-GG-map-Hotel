# app_ai.py

import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
from openai_utils import OpenAIAssistant
import numpy as np


def load_data_csv(file_path):
    return pd.read_csv(file_path)

def load_data_excel(file_path):
    return pd.read_excel(file_path)

def display_data(data):
    if not data.empty:
        st.write("Dữ liệu mẫu:")
        rows_per_page = 20
        total_rows = len(data)
        num_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
        page = st.number_input("Chọn trang: ", min_value=1, max_value=num_pages, step=1)
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        st.write(data.iloc[start_idx:end_idx])

def execute_code(code, data):
    try:
        local_scope = {'np': np, 'data': data, 'plt': plt}
        exec(code, {}, local_scope)
        if 'plt' in local_scope:
            st.pyplot(local_scope['plt'].gcf())  # Display the generated plot
        else:
            st.error("Không tìm thấy đối tượng plt để hiển thị biểu đồ.")
    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi thực thi mã: {e}")

def main():
    # Load data from an Excel file
    file_path = "4star_hotels.xlsx"
    data = load_data_excel(file_path)

    # Streamlit UI
    st.title("Pyplot Chart Generator")
    user_input = st.text_area("Enter your chart request:")

    # Display sample data
    display_data(data)

    # Get column names
    columns = data.columns

    # Initialize OpenAIAssistant with custom instructions
    init_instruction = "You are an experienced programmer, especially in data analysis and visualization using Pyplot."
    assistant = OpenAIAssistant(model_name="gpt-4o", init_instruction=init_instruction)
    assistant_msg = "Analyse the user's request, choose the best chart type, and generate Python code to plot the chart."
    assistant.add_message('assistant', assistant_msg)

    if st.button("Generate Chart"):
        if user_input:
            # Create prompt for OpenAI API
            prompt = f'Create a Python code to plot a chart using Pyplot for the following request: "{user_input}". Given data columns: {columns}. Data is stored in a DataFrame named "data" so do not create sample data, just assume data is there.'
            try:
                # Get code response from OpenAI
                response = assistant.answer(prompt)
                code = response.split('```python')[1].split('```')[0].strip()  # Extract code from response
                # Execute the generated code
                execute_code(code, data)
            except Exception as e:
                st.error(f"Đã xảy ra lỗi khi thực thi mã: {e}")
        else:
            st.warning("Vui lòng nhập yêu cầu.")

if __name__ == "__main__":
    main()
