import { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8004/fazendas';

export function useFarms() {
	const [activeTab, setActiveTab] = useState('radius');
	const [pos, setPos] = useState({ lat: -21.45, lon: -51.045 });
	const [radius, setRadius] = useState(5);
	const [farmId, setFarmId] = useState(''); // farmId definido aqui
	const [results, setResults] = useState([]);
	const [loading, setLoading] = useState(false);
	const [page, setPage] = useState(1);
	const [hasMore, setHasMore] = useState(true);
	const PAGE_SIZE = 20;

	const handleSearch = async (isNewSearch = true) => {
		setLoading(true);
		const searchPage = isNewSearch ? 1 : page;

		if (isNewSearch) {
			setResults([]);
			setHasMore(true);
		}

		try {
			let response;
			if (activeTab === 'id') {
				// Agora o farmId está acessível aqui dentro
				const url = `${API_BASE}/${farmId.trim()}`;
				response = await axios.get(url);
				setResults([response.data]);
				setHasMore(false);
				if (response.data.geometry?.coordinates[0][0]) {
					const [lon, lat] = response.data.geometry.coordinates[0][0];
					setPos({ lat, lon });
				}
			} else {
				const endpoint = activeTab === 'point' ? 'busca-ponto' : 'busca-raio';
				const payload = {
					latitude: parseFloat(pos.lat),
					longitude: parseFloat(pos.lon),
					page: searchPage,
					size: PAGE_SIZE,
					...(activeTab === 'radius' && { radius_km: parseFloat(radius) })
				};

				response = await axios.post(`${API_BASE}/${endpoint}`, payload);
				const newFarms = response.data;

				if (newFarms.length < PAGE_SIZE) setHasMore(false);
				setResults(prev => isNewSearch ? newFarms : [...prev, ...newFarms]);
				setPage(searchPage + 1);
			}
		} catch (error) {
			console.error(error);
			alert("Erro na busca. Verifique o ID ou conexão.");
		} finally {
			setLoading(false);
		}
	};

	return {
		activeTab, setActiveTab,
		pos, setPos,
		radius, setRadius,
		farmId, setFarmId,
		results, loading,
		hasMore, handleSearch
	};
}