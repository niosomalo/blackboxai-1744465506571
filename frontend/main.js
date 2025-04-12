// API Base URL
const API_URL = '/api';

// Utility Functions
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alertClass = type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
    
    alertContainer.innerHTML = `
        <div class="rounded-md p-4 ${alertClass}">
            <div class="flex">
                <div class="flex-shrink-0">
                    <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <div class="-mx-1.5 -my-1.5">
                        <button onclick="this.parentElement.parentElement.parentElement.parentElement.classList.add('hidden')" class="inline-flex rounded-md p-1.5 ${alertClass} hover:bg-${type === 'success' ? 'green' : 'red'}-200 focus:outline-none">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    alertContainer.classList.remove('hidden');
}

function formatPrice(price) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR'
    }).format(price);
}

// Bahan (Raw Materials) Page Functions
if (window.location.pathname.includes('bahan.html')) {
    // Load bahan data
    async function loadBahanData() {
        try {
            const response = await fetch(`${API_URL}/bahan`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const tableBody = document.getElementById('bahanTable');
                tableBody.innerHTML = data.data.map(bahan => `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            ${bahan.nama_bahan}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${bahan.satuan}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${bahan.stok_awal}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${formatPrice(bahan.harga_per_gram)}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button onclick="editBahan(${bahan.id_bahan})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteBahan(${bahan.id_bahan})" class="text-red-600 hover:text-red-900">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            showAlert('Failed to load bahan data', 'error');
        }
    }

    // Initialize bahan page
    window.addEventListener('load', loadBahanData);

    // Modal functions
    window.openAddModal = function() {
        document.getElementById('modalTitle').textContent = 'Tambah Bahan Baku';
        document.getElementById('bahanForm').reset();
        document.getElementById('bahanId').value = '';
        document.getElementById('bahanModal').classList.remove('hidden');
    }

    window.closeModal = function() {
        document.getElementById('bahanModal').classList.add('hidden');
    }

    window.handleSubmit = async function(event) {
        event.preventDefault();
        const formData = {
            nama_bahan: document.getElementById('namaBahan').value,
            satuan: document.getElementById('satuan').value,
            stok_awal: parseFloat(document.getElementById('stokAwal').value),
            harga_per_gram: parseFloat(document.getElementById('hargaPerGram').value)
        };
        
        const bahanId = document.getElementById('bahanId').value;
        const method = bahanId ? 'PUT' : 'POST';
        const url = bahanId ? `${API_URL}/bahan/${bahanId}` : `${API_URL}/bahan`;
        
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                showAlert(bahanId ? 'Bahan updated successfully' : 'Bahan added successfully');
                closeModal();
                loadBahanData();
            } else {
                showAlert(data.message, 'error');
            }
        } catch (error) {
            showAlert('Failed to save bahan', 'error');
        }
    }
}

// Menu Page Functions
if (window.location.pathname.includes('menu.html')) {
    let bahanList = [];

    // Initialize page
    document.addEventListener('DOMContentLoaded', async () => {
        await loadBahanData();
        await loadMenuData();
    });

    // Load menu data
    async function loadMenuData() {
        try {
            const response = await fetch(`${API_URL}/menu`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const menuContainer = document.getElementById('menuContainer');
                menuContainer.innerHTML = data.data.map(menu => `
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-4 py-5 sm:p-6">
                            <div class="flex items-center justify-between mb-4">
                                <h3 class="text-lg font-medium text-gray-900">
                                    ${menu.nama_menu}
                                </h3>
                                <div>
                                    <button onclick="editMenu(${menu.id_menu})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button onclick="deleteMenu(${menu.id_menu})" class="text-red-600 hover:text-red-900">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="space-y-2">
                                ${menu.resep.map(item => `
                                    <div class="flex justify-between text-sm">
                                        <span class="text-gray-500">${item.bahan.nama_bahan}</span>
                                        <span class="text-gray-900">${item.jumlah} ${item.bahan.satuan} (${item.waste_percent}% waste)</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            showAlert('Failed to load menu data', 'error');
        }
    }

    // Load bahan data for dropdowns
    async function loadBahanData() {
        try {
            const response = await fetch(`${API_URL}/bahan`);
            const data = await response.json();
            
            if (data.status === 'success') {
                bahanList = data.data;
                console.log('Loaded bahan data:', bahanList);
                // Update any existing recipe items
                const selects = document.querySelectorAll('.resep-item select');
                console.log('Found select elements:', selects.length);
                selects.forEach(select => {
                    populateBahanDropdown(select);
                });
            }
        } catch (error) {
            console.error('Failed to load bahan data:', error);
            showAlert('Failed to load bahan data', 'error');
        }
    }


    window.populateBahanDropdown = function(select) {
        // Clear existing options
        select.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Pilih Bahan';
        select.appendChild(defaultOption);
        
        // Add bahan options
        bahanList.forEach(bahan => {
            const option = document.createElement('option');
            option.value = bahan.id_bahan;
            option.textContent = `${bahan.nama_bahan} (${bahan.satuan})`;
            select.appendChild(option);
        });
    }

    window.addResepItem = function() {
        const template = document.getElementById('resepItemTemplate');
        const container = document.getElementById('resepContainer');
        const clone = template.content.cloneNode(true);
        
        // Populate bahan dropdown
        const select = clone.querySelector('select');
        populateBahanDropdown(select);
        
        container.appendChild(clone);
    }

    window.removeResepItem = function(button) {
        button.closest('.resep-item').remove();
    }

    // Modal functions
    window.openAddModal = function() {
        document.getElementById('modalTitle').textContent = 'Tambah Menu';
        document.getElementById('menuForm').reset();
        document.getElementById('menuId').value = '';
        document.getElementById('menuModal').classList.remove('hidden');
        
        // Clear existing recipe items
        const container = document.getElementById('resepContainer');
        container.innerHTML = '';
        
        // Add one empty recipe item by default
        const template = document.getElementById('resepItemTemplate');
        const clone = template.content.cloneNode(true);
        
        // Get the select element and populate it
        const select = clone.querySelector('select');
        populateBahanDropdown(select);
        
        container.appendChild(clone);
    }

    window.closeModal = function() {
        document.getElementById('menuModal').classList.add('hidden');
    }

    window.handleSubmit = async function(event) {
        event.preventDefault();
        const formData = {
            nama_menu: document.getElementById('namaMenu').value,
            resep: Array.from(document.querySelectorAll('.resep-item')).map(item => ({
                id_bahan: parseInt(item.querySelector('select[name="bahan[]"]').value),
                jumlah: parseFloat(item.querySelector('input[name="jumlah[]"]').value),
                waste_percent: parseFloat(item.querySelector('input[name="waste[]"]').value)
            }))
        };
        
        const menuId = document.getElementById('menuId').value;
        const method = menuId ? 'PUT' : 'POST';
        const url = menuId ? `${API_URL}/menu/${menuId}` : `${API_URL}/menu`;
        
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                showAlert(menuId ? 'Menu updated successfully' : 'Menu added successfully');
                closeModal();
                loadMenuData();
            } else {
                showAlert(data.message, 'error');
            }
        } catch (error) {
            showAlert('Failed to save menu', 'error');
        }
    }

    window.editMenu = async function(menuId) {
        try {
            const response = await fetch(`${API_URL}/menu/${menuId}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const menu = data.data;
                document.getElementById('modalTitle').textContent = 'Edit Menu';
                document.getElementById('menuId').value = menu.id_menu;
                document.getElementById('namaMenu').value = menu.nama_menu;
                
                // Clear and populate recipe items
                const container = document.getElementById('resepContainer');
                container.innerHTML = '';
                
                menu.resep.forEach(item => {
                    const template = document.getElementById('resepItemTemplate');
                    const clone = template.content.cloneNode(true);
                    
                    const select = clone.querySelector('select');
                    populateBahanDropdown(select);
                    select.value = item.id_bahan;
                    
                    clone.querySelector('input[name="jumlah[]"]').value = item.jumlah;
                    clone.querySelector('input[name="waste[]"]').value = item.waste_percent;
                    
                    container.appendChild(clone);
                });
                
                document.getElementById('menuModal').classList.remove('hidden');
            }
        } catch (error) {
            showAlert('Failed to load menu data', 'error');
        }
    }

    window.deleteMenu = async function(menuId) {
        if (confirm('Are you sure you want to delete this menu?')) {
            try {
                const response = await fetch(`${API_URL}/menu/${menuId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    showAlert('Menu deleted successfully');
                    loadMenuData();
                } else {
                    showAlert(data.message, 'error');
                }
            } catch (error) {
                showAlert('Failed to delete menu', 'error');
            }
        }
    }
}

// Penjualan (Sales) Page Functions
if (window.location.pathname.includes('penjualan.html')) {
    let menuList = [];

    // Load menu data for dropdown
    async function loadMenuData() {
        try {
            const response = await fetch(`${API_URL}/menu`);
            const data = await response.json();
            
            if (data.status === 'success') {
                menuList = data.data;
                const menuSelect = document.getElementById('menu');
                menuSelect.innerHTML = `
                    <option value="">Pilih Menu</option>
                    ${menuList.map(menu => `
                        <option value="${menu.id_menu}">${menu.nama_menu}</option>
                    `).join('')}
                `;
            }
        } catch (error) {
            showAlert('Failed to load menu data', 'error');
        }
    }

    // Load today's sales
    async function loadTodaysSales() {
        const today = new Date().toISOString().split('T')[0];
        try {
            const response = await fetch(`${API_URL}/penjualan/daily/${today}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const salesHistory = document.getElementById('salesHistory');
                salesHistory.innerHTML = data.data.sales.map(sale => `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            ${sale.menu.nama_menu}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${sale.jumlah_terjual}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${formatPrice(sale.total_cost)}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${sale.total_waste} gr
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${new Date(sale.created_at).toLocaleTimeString()}
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            showAlert('Failed to load sales history', 'error');
        }
    }

    // Initialize sales page
    window.addEventListener('load', () => {
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('tanggal').value = today;
        
        loadMenuData();
        loadTodaysSales();
    });

    // Handle sales form submission
    async function handleSubmit(event) {
        event.preventDefault();
        const formData = {
            id_menu: parseInt(document.getElementById('menu').value),
            tanggal: document.getElementById('tanggal').value,
            jumlah_terjual: parseInt(document.getElementById('jumlah').value)
        };
        
        try {
            const response = await fetch(`${API_URL}/penjualan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                showAlert('Penjualan recorded successfully');
                document.getElementById('penjualanForm').reset();
                document.getElementById('tanggal').value = new Date().toISOString().split('T')[0];
                
                // Show results
                document.getElementById('salesResult').classList.remove('hidden');
                document.getElementById('totalCogs').textContent = formatPrice(data.data.total_cost);
                
                const usageDetails = document.getElementById('usageDetails');
                usageDetails.innerHTML = data.data.usage_details.map(usage => `
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-500">${usage.bahan.nama_bahan}</span>
                        <span class="text-gray-900">
                            ${usage.jumlah_terpakai} ${usage.bahan.satuan}
                            (waste: ${usage.jumlah_waste} ${usage.bahan.satuan})
                        </span>
                    </div>
                `).join('');
                
                // Reload sales history
                loadTodaysSales();
            } else {
                showAlert(data.message, 'error');
            }
        } catch (error) {
            showAlert('Failed to record sale', 'error');
        }
    }
}

// Dashboard Page Functions
if (window.location.pathname === '/' || window.location.pathname.includes('index.html')) {
    async function loadDashboardData() {
        const today = new Date().toISOString().split('T')[0];
        try {
            // Load today's summary
            const response = await fetch(`${API_URL}/penjualan/daily/${today}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                document.getElementById('totalSales').textContent = data.data.total_sales;
                document.getElementById('totalCogs').textContent = formatPrice(data.data.total_cost);
                document.getElementById('totalWaste').textContent = `${data.data.total_waste} gr`;
            }
            
            // Load low stock items
            const bahanResponse = await fetch(`${API_URL}/bahan`);
            const bahanData = await bahanResponse.json();
            
            if (bahanData.status === 'success') {
                const lowStockItems = bahanData.data.filter(bahan => bahan.stok_awal < 1000); // Example threshold
                document.getElementById('lowStockCount').textContent = lowStockItems.length;
                
                const lowStockTable = document.getElementById('lowStockTable');
                lowStockTable.innerHTML = lowStockItems.map(bahan => `
                    <tr>
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            ${bahan.nama_bahan}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${bahan.stok_awal} ${bahan.satuan}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${bahan.satuan}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                                Low Stock
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            showAlert('Failed to load dashboard data', 'error');
        }
    }

    // Initialize dashboard
    window.addEventListener('load', loadDashboardData);
}
