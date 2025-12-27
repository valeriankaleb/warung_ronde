function updateCart(id) {
    // 1. Update Tampilan Total Harga di Layar (Frontend)
    updateTotal();

    // 2. Ambil nilai terbaru dari input
    let input = document.getElementById('jumlah_' + id);
    let quantity = input.value;

    // 3. Kirim data terbaru ke Server Python (Backend)
    fetch('/update_item_quantity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: id,
            jumlah: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server updated:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Fungsi untuk mengupdate total harga
function updateTotal() {
    let total = 0;
    const items = document.querySelectorAll('.row.mb-4'); // Ambil semua item di cart

    items.forEach(item => {
        const jumlah = item.querySelector('input[type=number]').value; // Ambil jumlah
        const harga = item.querySelector('.item-harga').value; // Ambil harga
        total += jumlah * harga; // Hitung total
    });

    document.getElementById('total_harga').innerText = 'Rp.' + total; // Update total harga
    document.getElementById('total_harga2').innerText = 'Rp.' + total;
}

// Event listener untuk setiap input jumlah
document.querySelectorAll('input[type=number]').forEach(input => {
    input.addEventListener('change', updateTotal); // Update total saat jumlah berubah
    input.addEventListener('input', updateTotal); // Tambahkan event listener untuk input
});

// Tambahkan event listener untuk tombol "+" dan "-"
document.querySelectorAll('.btn-primary').forEach(button => {
    button.addEventListener('click', updateTotal); // Update total saat tombol "+" atau "-" diklik
});

// Panggil updateTotal saat halaman dimuat
document.addEventListener('DOMContentLoaded', updateTotal);

// Fungsi untuk menghapus item
function removeItem(id) {
    // Menghapus item dari cart (kirim request ke server)
    fetch(`/remove_from_cart/${id}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                location.reload(); // Reload halaman untuk mendapatkan total harga yang baru
            }
        });
}

function updateTotal() {
    let total = 0;
    const items = document.querySelectorAll('.row.mb-4'); // Ambil semua item di cart
    const checkboxPoin = document.getElementById('tukar_poin'); // Ambil checkbox poin
    const isPoinUsed = checkboxPoin && checkboxPoin.checked; // Cek apakah checkbox ada dan dicentang

    items.forEach((item, index) => {
        const inputJumlah = item.querySelector('input[type=number]');
        const jumlah = parseInt(inputJumlah.value);
        const inputHarga = item.querySelector('.item-harga');
        const harga = parseFloat(inputHarga.value);
        const displayHarga = item.querySelector('.price-display'); // Elemen teks harga yg kita tambah class tadi

        let subtotal = jumlah * harga;

        // Logika Diskon Poin: Hanya berlaku untuk item PERTAMA (index 0)
        if (isPoinUsed && index === 0) {
            // Hitung total dikurangi harga 1 unit barang pertama
            // (Jika beli 2, yg gratis cuma 1)
            total += subtotal - harga;

            // UBAH TAMPILAN VISUAL: Coret harga asli, tampilkan badge Gratis
            displayHarga.innerHTML = `
                <span class="text-decoration-line-through text-muted small">Rp.${harga}</span>
                <span class="badge bg-success ms-1">GRATIS (Poin)</span>
            `;
        } else {
            // Jika tidak pakai poin atau bukan item pertama
            total += subtotal;

            // KEMBALIKAN TAMPILAN NORMAL
            displayHarga.innerText = 'Rp.' + harga;
        }
    });

    // Pastikan total tidak minus
    if (total < 0) total = 0;

    // Update teks total harga di bawah
    const totalText = 'Rp.' + total;
    if (document.getElementById('total_harga')) {
        document.getElementById('total_harga').innerText = totalText;
    }
    if (document.getElementById('total_harga2')) {
        document.getElementById('total_harga2').innerText = totalText;
    }
}

// Event listener untuk setiap input jumlah (Quantity)
document.querySelectorAll('input[type=number]').forEach(input => {
    input.addEventListener('change', updateTotal);
    input.addEventListener('input', updateTotal);
});

// Event listener untuk tombol "+" dan "-"
document.querySelectorAll('.btn-primary').forEach(button => {
    button.addEventListener('click', () => {
        // Beri sedikit delay agar value input terupdate dulu oleh event click bawaan
        setTimeout(updateTotal, 50);
    });
});

// TAMBAHAN: Event listener untuk Checkbox Poin
const checkboxPoin = document.getElementById('tukar_poin');
if (checkboxPoin) {
    checkboxPoin.addEventListener('change', updateTotal);
}

// Panggil updateTotal saat halaman dimuat pertama kali
document.addEventListener('DOMContentLoaded', updateTotal);

// Fungsi untuk menghapus item
function removeItem(id) {
    if (!confirm("Hapus item ini dari keranjang?")) return;

    fetch(`/remove_from_cart/${id}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                location.reload();
            }
        });

window.onpageshow = function(event) {
        if (event.persisted) {
            // Jika terdeteksi dari cache, paksa reload halaman
            window.location.reload();
        }
    };
}