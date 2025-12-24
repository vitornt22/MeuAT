import React from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, Circle, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useFarms } from './hooks/useFarms';

// Leaflet icon correction
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function ChangeView({ center }) {
  const map = useMap();
  map.setView(center, map.getZoom());
  return null;
}

function App() {
  const {
    activeTab, setActiveTab,
    pos, setPos,
    radius, setRadius,
    farmId, setFarmId,
    results, loading,
    hasMore, handleSearch
  } = useFarms();

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f4f7f6' }}>

      {/* SIDEBAR */}
      <div style={sidebarStyle}>
        <h2 style={{ color: '#2c3e50', marginBottom: '5px' }}>🛰️ MeuAT Monitor</h2>
        <p style={{ fontSize: '12px', color: '#7f8c8d', marginBottom: '20px' }}>Sistema de Gestão Geospacial</p>

        {/* Tabs Selection */}
        <div style={{ display: 'flex', gap: '5px', marginBottom: '20px' }}>
          {['radius', 'point', 'id'].map(t => (
            <button key={t} onClick={() => setActiveTab(t)} style={tabStyle(activeTab === t)}>
              {t.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Search Form */}
        <div style={cardStyle}>
          {activeTab === 'id' ? (
            <input style={inputStyle} placeholder="ID (CAR)" value={farmId} onChange={e => setFarmId(e.target.value)} />
          ) : (
            <>
              <label style={labelStyle}>Latitude</label>
              <input style={inputStyle} type="number" value={pos.lat} onChange={e => setPos({ ...pos, lat: e.target.value })} />
              <label style={labelStyle}>Longitude</label>
              <input style={inputStyle} type="number" value={pos.lon} onChange={e => setPos({ ...pos, lon: e.target.value })} />
              {activeTab === 'radius' && (
                <>
                  <label style={labelStyle}>Raio (km)</label>
                  <input style={inputStyle} type="number" value={radius} onChange={e => setRadius(e.target.value)} />
                </>
              )}
            </>
          )}
          <button onClick={() => handleSearch(true)} disabled={loading} style={searchBtnStyle}>
            {loading ? 'Carregando...' : '🔍 Pesquisar'}
          </button>
        </div>

        {/* Results List and Pagination */}
        <div style={{ marginTop: '20px' }}>
          <h4 style={{ borderBottom: '1px solid #ddd', paddingBottom: '5px' }}>Resultados ({results.length})</h4>
          <div style={resultsListStyle}>
            {results.map((f, i) => (
              <div key={i} style={resultItemStyle}>
                <small style={{ color: '#2980b9', fontWeight: 'bold' }}>{f.imovel_code.substring(0, 15)}...</small>
                <div style={{ fontSize: '13px' }}>{f.city} - {f.state_code}</div>
              </div>
            ))}
          </div>

          {hasMore && results.length >= 20 && (
            <button onClick={() => handleSearch(false)} disabled={loading} style={loadMoreStyle}>
              {loading ? 'Buscando mais...' : 'Carregar Próxima Página'}
            </button>
          )}
        </div>
      </div>

      {/* MAPA */}
      <div style={{ flex: 1 }}>
        <MapContainer center={[pos.lat, pos.lon]} zoom={12} style={{ height: '100%', width: '100%' }}>
          <ChangeView center={[pos.lat, pos.lon]} />
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {activeTab !== 'id' && <Marker position={[pos.lat, pos.lon]}><Popup>Origem</Popup></Marker>}

          {activeTab === 'radius' && (
            <Circle center={[pos.lat, pos.lon]} radius={radius * 1000} pathOptions={{ color: '#3498db', fillOpacity: 0.1 }} />
          )}

          {results.map((f, i) => (
            <GeoJSON
              key={`${f.imovel_code}-${i}`}
              data={f.geometry}
              style={{ color: '#27ae60', weight: 2, fillOpacity: 0.4 }}
              onEachFeature={(feat, layer) => {
                layer.bindPopup(`<b>Código:</b> ${f.imovel_code}<br><b>Área:</b> ${f.area_size} ha`);
              }}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

// ESTILOS INLINE
const sidebarStyle = { width: '360px', padding: '20px', background: '#fff', borderRight: '1px solid #ddd', overflowY: 'auto' };
const cardStyle = { background: '#f9f9f9', padding: '15px', borderRadius: '8px', border: '1px solid #eee' };
const inputStyle = { width: '100%', padding: '10px', marginBottom: '12px', borderRadius: '4px', border: '1px solid #ccc', boxSizing: 'border-box' };
const labelStyle = { fontSize: '12px', fontWeight: 'bold', color: '#34495e' };
const searchBtnStyle = { width: '100%', padding: '12px', backgroundColor: '#2ecc71', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' };
const loadMoreStyle = { width: '100%', padding: '10px', marginTop: '10px', backgroundColor: '#3498db', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' };
const tabStyle = (active) => ({ flex: 1, padding: '10px', cursor: 'pointer', border: 'none', borderRadius: '4px', backgroundColor: active ? '#34495e' : '#ecf0f1', color: active ? '#fff' : '#7f8c8d', fontWeight: 'bold' });
const resultsListStyle = { maxHeight: '300px', overflowY: 'auto', marginTop: '10px' };
const resultItemStyle = { padding: '10px', borderBottom: '1px solid #eee', backgroundColor: '#fff' };

export default App;