document.addEventListener('DOMContentLoaded', async () => {
    async function fetchData(url) {
        const response = await fetch(url);
        return response.json();
    }

    const indexes = await fetchData('/json/ubuntu_indexes.json');
    const repoSize = await fetchData('/json/ubuntu_reposize.json');

    let totalPackages = 0;
    let totalSources = 0;
    let totalSize = 0;
    let totalSourceSize = 0;

    const tableBody = document.getElementById('repo-stats-body');

    for (const [release, components] of Object.entries(repoSize)) {
        let releaseTotal = 0;
        let releaseSourceTotal = 0;
        let releasePackages = 0;
        let releaseSources = 0;

        for (const [component, data] of Object.entries(components)) {
            for (const [arch, stats] of Object.entries(data)) {
                if (arch.startsWith('binary')) {
                    releasePackages += stats.packages || 0;
                    releaseTotal += stats.total_size || 0;
                } else if (arch === 'source') {
                    releaseSources += stats.projects || 0;
                    releaseSourceTotal += stats.source_size || 0;
                }
            }
        }

        totalPackages += releasePackages;
        totalSources += releaseSources;
        totalSize += releaseTotal;
        totalSourceSize += releaseSourceTotal;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${release}</td>
            <td>${releasePackages.toLocaleString()}</td>
            <td>${(releaseTotal / (1024 ** 3)).toFixed(2)} GB</td>
            <td>${releaseSources.toLocaleString()}</td>
            <td>${(releaseSourceTotal / (1024 ** 3)).toFixed(2)} GB</td>
        `;
        tableBody.appendChild(row);
    }

    document.getElementById('total-packages').textContent = totalPackages.toLocaleString();
    document.getElementById('total-sources').textContent = totalSources.toLocaleString();
    document.getElementById('total-size').textContent = (totalSize / (1024 ** 3)).toFixed(2) + ' GB';
    document.getElementById('total-source-size').textContent = (totalSourceSize / (1024 ** 3)).toFixed(2) + ' GB';
});

