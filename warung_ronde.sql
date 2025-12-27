-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 27, 2025 at 12:42 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `warung_ronde`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbpesanan`
--

CREATE TABLE `tbpesanan` (
  `id_pesanan` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `nomorHP` varchar(255) NOT NULL,
  `item_pesanan` varchar(255) NOT NULL,
  `tanggal_pesanan` datetime NOT NULL,
  `modifikasi` text NOT NULL,
  `total_harga` decimal(10,2) NOT NULL,
  `status` enum('Menunggu','Diproses','Diantar','Selesai') NOT NULL,
  `alamat` text NOT NULL,
  `metode_pembayaran` enum('transfer_bank','qris','tunai','e-wallet') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbpesanan`
--

INSERT INTO `tbpesanan` (`id_pesanan`, `id_user`, `username`, `nomorHP`, `item_pesanan`, `tanggal_pesanan`, `modifikasi`, `total_harga`, `status`, `alamat`, `metode_pembayaran`) VALUES
(55, 18, 'valerian', '', 'Wedang Kacang (2), Wedang Roti (2), Wedang Ronde (1)', '2025-12-16 14:38:38', 'Biji', 60000.00, 'Menunggu', 'Jl. Tidar No.44, Kemirirejo, Kec. Magelang Tengah, Kota Magelang, Jawa Tengah 59214', 'qris'),
(56, 18, 'valerian', '', 'Wedang Kacang (4), Wedang Roti (2)', '2025-12-16 14:40:50', '', 60000.00, 'Selesai', 'jl.kecamatan fajar no.46', 'tunai');

-- --------------------------------------------------------

--
-- Table structure for table `tbproduk`
--

CREATE TABLE `tbproduk` (
  `id` int(11) NOT NULL,
  `nama` varchar(255) NOT NULL,
  `harga` decimal(10,2) NOT NULL,
  `foto` varchar(255) DEFAULT NULL,
  `detail` text DEFAULT NULL,
  `stok` enum('Habis','Tersedia') DEFAULT 'Tersedia'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbproduk`
--

INSERT INTO `tbproduk` (`id`, `nama`, `harga`, `foto`, `detail`, `stok`) VALUES
(2, 'Wedang Ronde', 10000.00, 'aTpL6faU4ZC4Sjd4dPUx.png', 'Minuman tradisional Indonesia yang kaya akan rempah. Kuah jahe yang hangat berpadu sempurna dengan kenyalnya ronde berisi kacang. Sajian sempurna untuk menghangatkan tubuh di cuaca dingin.', 'Tersedia'),
(3, 'Wedang Kacang', 10000.00, 'QCdzUZxcPtZWKH2TUx86.png', 'Minuman tradisional Jawa yang kaya akan cita rasa. Kacang tanah yang lembut berpadu sempurna dengan kuah santan gurih dan manisnya gula jawa. Sajian hangat yang cocok untuk menemani hari-hari santai.', 'Tersedia'),
(4, 'Wedang Roti', 10000.00, 'hjcaoW9w7tp9565SbdY9.png', 'Minuman tradisional Indonesia yang kaya akan cita rasa. Roti tawar yang lembut berpadu sempurna dengan kuah santan gurih dan manisnya gula jawa. Sajian hangat yang cocok untuk menemani hari-hari santai.', 'Tersedia'),
(5, 'Sup Jagung', 10000.00, 'FF4Ri7LQ1nSF3OaNd8Hq.png', 'Sup kental hangat yang disajikan memakai jagung sebagai bahan utama. Bahan sup jagung kental dasar terdiri dari jagung, bawang bombay, dan seledri.', 'Tersedia'),
(6, 'Nasi Goreng', 18000.00, '9QhQrwd9is1mid4Pk9Z0.png', 'Berupa nasi yang digoreng dan dicampur dalam minyak goreng. Ditambah dengan kecap manis, bawang merah, bawang putih, asam jawa, lada dan bahan lainnya; seperti telur, daging ayam, dan kerupuk.', 'Tersedia'),
(8, 'Bakmi Goreng', 18000.00, '0felXT48S2Q65GhBpOy4.png', 'Terbuat dari mie kuning yang digoreng dengan bumbu-bumbu khas, seperti bawang merah, bawang putih, kecap manis, cabe merah, dengan tambahan daging ayam, telur, tomat, kubis, mentimun dan bumbu-bumbu lainnya.                                                                        ', 'Tersedia'),
(25, 'Nasi Godog', 18000.00, 'ujLukBiIER.png', 'Perpaduan nasi pulen yang dimasak perlahan dalam kuah kaldu gurih yang \"nyemek\" (kental), menyatu sempurna dengan telur kocok yang lembut. Dilengkapi dengan irisan sayuran hijau segar, potongan tomat yang memberi sentuhan asam segar, serta suwiran ayam kampung. Tak lupa, taburan bawang goreng melimpah di atasnya memberikan aroma harum yang tak tertahankan. Sangat cocok dinikmati saat cuaca dingin atau kapan pun Anda butuh asupan yang menghangatkan hati dan perut.', 'Tersedia'),
(26, 'Mie Godog', 18000.00, 'LcIxXKfWw4.png', 'Perpaduan sempurna antara mie kuning yang kenyal dan bihun lembut, bermandi kuah kaldu telur yang creamy dan gurih. Menyajikannya dengan potongan daging ayam rebus yang tebal dan juicy (bukan suwiran kering), memberikan kepuasan di setiap gigitan. Dilengkapi dengan renyahnya sayuran segar, irisan tomat, dan taburan bawang goreng yang melimpah.', 'Tersedia');

-- --------------------------------------------------------

--
-- Table structure for table `tbreview`
--

CREATE TABLE `tbreview` (
  `id_review` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `id_produk` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `komentar` text DEFAULT NULL,
  `tanggal` datetime DEFAULT current_timestamp(),
  `balasan` text DEFAULT NULL,
  `tanggal_balasan` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbreview`
--

INSERT INTO `tbreview` (`id_review`, `id_user`, `id_produk`, `rating`, `komentar`, `tanggal`, `balasan`, `tanggal_balasan`) VALUES
(4, 18, 3, 5, 'Testw', '2025-12-16 14:37:49', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbuser`
--

CREATE TABLE `tbuser` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(50) NOT NULL,
  `nomorHP` varchar(15) NOT NULL,
  `role` enum('admin','user') NOT NULL,
  `poin` int(11) DEFAULT 0,
  `foto_profil` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbuser`
--

INSERT INTO `tbuser` (`id_user`, `username`, `password`, `email`, `nomorHP`, `role`, `poin`, `foto_profil`) VALUES
(1, 'admin', 'scrypt:32768:8:1$fW2brQMe6kH7zjyN$d29ac31bac9ac30597345acda869a44d8d545d86316e5ec3b94c8e0e81d9eb0d82aa7063f39e35ae2f7a50989cd97b0913cf301d560f0db3c87bfa9f1b4a00d6', 'valekaleb46@gmail.com', '087708773589', 'admin', 0, NULL),
(18, 'valerian', 'scrypt:32768:8:1$vMyj2ATvyErBXmea$025fcfa2bec93bf5db1fb28f295f0aad5c472db4ae5f5baef92b95ca4676b5e6466a755302c100882c69e90663f79ed27f99a41d94123a155fdc7926f615c57c', 'valeriankaleb@students.amikom.ac.id', '087233339999', 'user', 2, NULL),
(20, 'ichiga', 'scrypt:32768:8:1$OlZzCiriXrlWSH1J$14bd58d197d3ed1cdf1c2398bed5e201cd05b887145527e1b8b3d36eded6aaa60545190704a4e40f217cbf4c08d71c480a01a25de85e70dbe12ab1818cb964ab', 'darkswagtnk@gmail.com', '087708773544', 'user', 0, 'Oqpc2cPEDl.jpg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbpesanan`
--
ALTER TABLE `tbpesanan`
  ADD PRIMARY KEY (`id_pesanan`),
  ADD KEY `id_user` (`id_user`) USING BTREE;

--
-- Indexes for table `tbproduk`
--
ALTER TABLE `tbproduk`
  ADD PRIMARY KEY (`id`),
  ADD KEY `nama` (`nama`);

--
-- Indexes for table `tbreview`
--
ALTER TABLE `tbreview`
  ADD PRIMARY KEY (`id_review`),
  ADD KEY `id_user` (`id_user`),
  ADD KEY `id_produk` (`id_produk`);

--
-- Indexes for table `tbuser`
--
ALTER TABLE `tbuser`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbpesanan`
--
ALTER TABLE `tbpesanan`
  MODIFY `id_pesanan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `tbproduk`
--
ALTER TABLE `tbproduk`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `tbreview`
--
ALTER TABLE `tbreview`
  MODIFY `id_review` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbuser`
--
ALTER TABLE `tbuser`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbpesanan`
--
ALTER TABLE `tbpesanan`
  ADD CONSTRAINT `tbpesanan_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `tbuser` (`id_user`);

--
-- Constraints for table `tbreview`
--
ALTER TABLE `tbreview`
  ADD CONSTRAINT `tbreview_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `tbuser` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `tbreview_ibfk_2` FOREIGN KEY (`id_produk`) REFERENCES `tbproduk` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
