// Custom JavaScript for Military Asset Management System

document.addEventListener('DOMContentLoaded', function() {
    console.log('Military Asset Management System loaded');

    // Add any custom JavaScript functionality here
    // For example, form validation, dynamic updates, etc.

    // Handle Net Movement Modal
    const netMovementModal = document.getElementById('netMovementModal');
    if (netMovementModal) {
        netMovementModal.addEventListener('show.bs.modal', function () {
            const content = document.getElementById('netMovementContent');
            content.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;

            // Get current filter parameters
            const urlParams = new URLSearchParams(window.location.search);
            const startDate = urlParams.get('start_date');
            const endDate = urlParams.get('end_date');

            let apiUrl = '/api/net-movement-details/';
            if (startDate || endDate) {
                apiUrl += '?' + new URLSearchParams({
                    start_date: startDate || '',
                    end_date: endDate || ''
                }).toString();
            }

            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    let html = '<div class="row">';
                    html += '<div class="col-md-4"><h6>Purchases</h6><ul class="list-group">';
                    data.purchases.forEach(purchase => {
                        html += `<li class="list-group-item">${purchase.asset__name}: ${purchase.quantity} on ${purchase.date}</li>`;
                    });
                    html += '</ul></div>';

                    html += '<div class="col-md-4"><h6>Transfers In</h6><ul class="list-group">';
                    data.transfers_in.forEach(transfer => {
                        html += `<li class="list-group-item">${transfer.asset__name}: ${transfer.quantity} from ${transfer.from_base__name} on ${transfer.timestamp}</li>`;
                    });
                    html += '</ul></div>';

                    html += '<div class="col-md-4"><h6>Transfers Out</h6><ul class="list-group">';
                    data.transfers_out.forEach(transfer => {
                        html += `<li class="list-group-item">${transfer.asset__name}: ${transfer.quantity} to ${transfer.to_base__name} on ${transfer.timestamp}</li>`;
                    });
                    html += '</ul></div>';

                    html += '</div>';
                    content.innerHTML = html;
                })
                .catch(error => {
                    content.innerHTML = '<p class="text-danger">Error loading data.</p>';
                    console.error('Error:', error);
                });
        });
    }
});
