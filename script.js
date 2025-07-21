document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const productUrlInput = document.getElementById('productUrl');
    const loader = document.getElementById('loader');
    const resultsContainer = document.getElementById('resultsContainer');
    const summaryContent = document.getElementById('summaryContent');
    const historyList = document.getElementById('historyList');

    const handleAnalysis = async () => {
        const url = productUrlInput.value.trim();
        if (!url) {
            alert('Lütfen bir ürün linki girin.');
            return;
        }

        loader.classList.remove('d-none');
        resultsContainer.classList.add('d-none');

        try {
            const response = await fetch(`/analyze?url=${encodeURIComponent(url)}`);
            const data = await response.json();

            if (response.ok) {
                summaryContent.textContent = data.summary;
                resultsContainer.classList.remove('d-none');
                addUrlToHistory(url);
            } else {
                alert(`Hata: ${data.error}`);
            }
        } catch (error) {
            console.error('Analiz sırasında bir hata oluştu:', error);
            alert('Analiz sırasında bir hata oluştu. Lütfen konsolu kontrol edin.');
        } finally {
            loader.classList.add('d-none');
        }
    };

    const addUrlToHistory = (url) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.textContent = url;
        historyList.prepend(listItem);
    };

    analyzeBtn.addEventListener('click', handleAnalysis);
});