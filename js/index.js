document.addEventListener('DOMContentLoaded', async () => {
    async function fetchData(url) {
        const response = await fetch(url);
        return response.json();
    }

    const repoSize = await fetchData('/json/ubuntu_reposize.json');

    let totalPackages = 0;
    let totalSources = 0;
    let totalSize = 0;
    let totalSourceSize = 0;

    const repoSizeTable = document.getElementById('repo-size-table');

    for (const [release, components] of Object.entries(repoSize)) {
        for (const [component, data] of Object.entries(components)) {
            for (const [arch, stats] of Object.entries(data)) {
                if (arch.startsWith('binary')) {
                    totalPackages += stats.packages || 0;
                    totalSize += stats.total_size || 0;

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${release}</td>
                        <td>${arch}</td>
                        <td>${(stats.total_size / (1024 ** 3)).toFixed(2)} GB</td>
                        <td>0 GB</td>
                    `;
                    repoSizeTable.appendChild(row);
                } else if (arch === 'source') {
                    totalSources += stats.projects || 0;
                    totalSourceSize += stats.source_size || 0;

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${release}</td>
                        <td>${arch}</td>
                        <td>0 GB</td>
                        <td>${(stats.source_size / (1024 ** 3)).toFixed(2)} GB</td>
                    `;
                    repoSizeTable.appendChild(row);
                }
            }
        }
    }

    document.getElementById('total-packages').textContent = totalPackages.toLocaleString();
    document.getElementById('total-sources').textContent = totalSources.toLocaleString();
    document.getElementById('total-size').textContent = (totalSize / (1024 ** 3)).toFixed(2) + ' GB';
    document.getElementById('total-source-size').textContent = (totalSourceSize / (1024 ** 3)).toFixed(2) + ' GB';
});
