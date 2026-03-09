import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Crop Protection Monitoring System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-card.temperature {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-card.humidity {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card.pesticide {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .status-safe {
        color: #00d084;
        font-weight: bold;
    }
    .status-warning {
        color: #ff9f43;
        font-weight: bold;
    }
    .status-danger {
        color: #ee5a6f;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Generate dummy sensor data
def generate_sensor_data():
    """Generate realistic dummy sensor data"""
    now = datetime.now()
    timestamps = [now - timedelta(hours=i) for i in range(24, 0, -1)]
    
    # Simulate temperature (15-35°C with daily variation)
    base_temp = 25 + 5 * np.sin(np.arange(24) * np.pi / 12)
    temperature = base_temp + np.random.normal(0, 1, 24)
    
    # Simulate humidity (40-90% with inverse correlation to temperature)
    base_humidity = 70 - 2 * (temperature - 25)
    humidity = np.clip(base_humidity + np.random.normal(0, 2, 24), 30, 100)
    
    # Simulate pesticide levels (0-100 ppm, spiked at certain times)
    pesticide = np.random.normal(30, 10, 24)
    pesticide[5:8] = np.random.normal(60, 5, 3)  # Morning spike
    pesticide[15:18] = np.random.normal(50, 5, 3)  # Evening spike
    pesticide = np.clip(pesticide, 0, 100)
    
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Temperature (°C)': temperature,
        'Humidity (%)': humidity,
        'Pesticide Level (ppm)': pesticide
    })
    
    return df

# Get current sensor values
def get_current_values(df):
    """Get the latest sensor readings"""
    latest = df.iloc[-1]
    return {
        'temperature': latest['Temperature (°C)'],
        'humidity': latest['Humidity (%)'],
        'pesticide': latest['Pesticide Level (ppm)']
    }

# Determine crop protection status
def get_protection_status(values):
    """Determine if crop is protected based on sensor readings"""
    temp = values['temperature']
    humidity = values['humidity']
    pesticide = values['pesticide']
    
    issues = []
    
    # Temperature thresholds
    if temp < 10 or temp > 40:
        issues.append("Temperature out of range")
    
    # Humidity thresholds (too dry or too wet)
    if humidity < 30 or humidity > 95:
        issues.append("Humidity out of range")
    
    # Pesticide coverage check
    if pesticide < 20:
        issues.append("Pesticide coverage insufficient")
    elif pesticide > 80:
        issues.append("Pesticide level too high")
    
    if not issues:
        return "PROTECTED", "✓ Optimal conditions", "status-safe"
    elif len(issues) == 1:
        return "WARNING", f"⚠ {issues[0]}", "status-warning"
    else:
        return "DANGER", f"✗ Multiple issues detected", "status-danger"

# Main app
def main():
    # Title and header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌾 Crop Protection Monitoring System")
        st.markdown("*IoT-based Real-time Monitoring Dashboard*")
    
    # Generate or load data
    if 'sensor_data' not in st.session_state:
        st.session_state.sensor_data = generate_sensor_data()
    
    df = st.session_state.sensor_data
    current_values = get_current_values(df)
    status, status_msg, status_class = get_protection_status(current_values)
    
    # Display current status
    st.markdown("---")
    
    # Status banner
    col_status = st.container()
    with col_status:
        st.markdown(f"<h2>Current Status: <span class='{status_class}'>{status}</span></h2>", unsafe_allow_html=True)
        st.markdown(f"<h3>{status_msg}</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Metrics cards row 1
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🌡️ Temperature",
            value=f"{current_values['temperature']:.1f}°C",
            delta=f"{current_values['temperature']-25:.1f}°C from ideal",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            label="💧 Humidity",
            value=f"{current_values['humidity']:.1f}%",
            delta=f"{current_values['humidity']-70:.1f}% from ideal",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            label="🧪 Pesticide Level",
            value=f"{current_values['pesticide']:.1f} ppm",
            delta=f"Coverage: {'Good' if 20 <= current_values['pesticide'] <= 80 else 'Poor'}",
            delta_color="off"
        )
    
    st.markdown("---")
    
    # Charts section
    st.subheader("📊 24-Hour Sensor Readings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["All Metrics", "Temperature", "Humidity", "Pesticide"])
    
    with tab1:
        # Create subplot figure with all metrics
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df['Temperature (°C)'],
            mode='lines+markers',
            name='Temperature (°C)',
            line=dict(color='#f5576c', width=2),
            yaxis='y1'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df['Humidity (%)'],
            mode='lines+markers',
            name='Humidity (%)',
            line=dict(color='#00f2fe', width=2),
            yaxis='y2'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Timestamp'],
            y=df['Pesticide Level (ppm)'],
            mode='lines+markers',
            name='Pesticide (ppm)',
            line=dict(color='#43e97b', width=2),
            yaxis='y3'
        ))
        
        fig.update_layout(
            title="All Sensor Metrics Over 24 Hours",
            xaxis=dict(title='Time'),
            yaxis=dict(title='Temperature (°C)', titlefont=dict(color='#f5576c')),
            yaxis2=dict(
                title='Humidity (%)',
                titlefont=dict(color='#00f2fe'),
                overlaying='y',
                side='left',
                anchor='free',
                position=0.0
            ),
            yaxis3=dict(
                title='Pesticide (ppm)',
                titlefont=dict(color='#43e97b'),
                overlaying='y',
                side='right',
                anchor='free',
                position=1.0
            ),
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig_temp = px.line(
            df,
            x='Timestamp',
            y='Temperature (°C)',
            title='Temperature Trends (24 Hours)',
            markers=True,
            line_shape='spline',
            template='plotly_white'
        )
        fig_temp.update_traces(line=dict(color='#f5576c', width=3))
        fig_temp.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="Ideal: 25°C")
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with tab3:
        fig_hum = px.line(
            df,
            x='Timestamp',
            y='Humidity (%)',
            title='Humidity Trends (24 Hours)',
            markers=True,
            line_shape='spline',
            template='plotly_white'
        )
        fig_hum.update_traces(line=dict(color='#00f2fe', width=3))
        fig_hum.add_hline(y=70, line_dash="dash", line_color="blue", annotation_text="Ideal: 70%")
        st.plotly_chart(fig_hum, use_container_width=True)
    
    with tab4:
        fig_pest = px.line(
            df,
            x='Timestamp',
            y='Pesticide Level (ppm)',
            title='Pesticide Level Trends (24 Hours)',
            markers=True,
            line_shape='spline',
            template='plotly_white'
        )
        fig_pest.update_traces(line=dict(color='#43e97b', width=3))
        fig_pest.add_hrange(20, 80, line_width=0, fillcolor="lightgreen", opacity=0.2, annotation_text="Safe Range")
        st.plotly_chart(fig_pest, use_container_width=True)
    
    st.markdown("---")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Control Panel")
    
    if st.sidebar.button("🔄 Refresh Sensor Data", key="refresh_btn"):
        st.session_state.sensor_data = generate_sensor_data()
        st.rerun()
    
    if st.sidebar.button("⚡ Simulate Real-Time Update", key="update_btn"):
        # Add one more data point
        last_row = st.session_state.sensor_data.iloc[-1].copy()
        new_time = last_row['Timestamp'] + timedelta(hours=1)
        new_row = pd.DataFrame({
            'Timestamp': [new_time],
            'Temperature (°C)': [last_row['Temperature (°C)'] + np.random.normal(0, 1)],
            'Humidity (%)': [np.clip(last_row['Humidity (%)'] + np.random.normal(0, 2), 30, 100)],
            'Pesticide Level (ppm)': [np.clip(last_row['Pesticide Level (ppm)'] + np.random.normal(0, 3), 0, 100)]
        })
        st.session_state.sensor_data = pd.concat([st.session_state.sensor_data, new_row], ignore_index=True)
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Safe Thresholds")
    st.sidebar.info("""
    **Temperature**: 10-40°C (Ideal: 25°C)
    
    **Humidity**: 30-95% (Ideal: 70%)
    
    **Pesticide**: 20-80 ppm (Safe Range)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Data Export")
    
    csv = df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="crop_monitoring_data.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Crop Protection Monitoring System v1.0 | IoT-based Real-time Monitoring
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
