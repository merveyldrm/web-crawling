# 🔥 Firebase Kurulum Adımları - Detaylı Rehber

## 🚀 1. Firebase Console'da Proje Oluşturma

### **Adım 1.1: Firebase Console'a Giriş**
1. Tarayıcınızda [Firebase Console](https://console.firebase.google.com) adresine gidin
2. Google hesabınızla giriş yapın
3. **"Add project"** (Proje Ekle) butonuna tıklayın

### **Adım 1.2: Proje Bilgilerini Girin**
1. **Project name**: `trendyol-comment-analysis` 
2. **Continue** butonuna tıklayın
3. Google Analytics'i etkinleştirin (opsiyonel)
4. **Create project** butonuna tıklayın

## 📊 2. Firestore Database Kurulumu

### **Adım 2.1: Firestore'u Etkinleştir**
1. Sol menüden **"Firestore Database"** seçin
2. **"Create database"** butonuna tıklayın
3. **"Start in test mode"** seçin (güvenlik kuralları daha sonra ayarlanacak)
4. **Next** butonuna tıklayın

### **Adım 2.2: Lokasyon Seçimi**
1. **Location**: `europe-west3 (Frankfurt)` seçin (Türkiye'ye en yakın)
2. **Done** butonuna tıklayın

## 🔑 3. Service Account Oluşturma

### **Adım 3.1: Project Settings'e Git**
1. Sol üst köşedeki ⚙️ (Settings) ikonuna tıklayın
2. **"Project settings"** seçin
3. **"Service accounts"** sekmesine tıklayın

### **Adım 3.2: Service Account Key Oluştur**
1. **"Generate new private key"** butonuna tıklayın
2. **"Generate key"** onayına tıklayın
3. JSON dosyası otomatik indirilecek
4. Dosya adını `trendyol-firebase-service-account.json` olarak değiştirin
5. Bu dosyayı proje klasörünüze (`D:\web-crawling\`) kopyalayın

## ✅ 4. Kurulum Doğrulaması

Dosya yapınız şöyle olmalı:
```
D:\web-crawling\
├── firebase_rag_integration.py
├── trendyol-firebase-service-account.json  ← Bu dosya olmalı
├── trendyol_comments.csv
└── diğer dosyalar...
``` 