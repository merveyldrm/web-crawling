import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os
from datetime import datetime

def test_firebase_connection(service_account_path=None):
    """Firebase bağlantısını test et"""
    
    print("🔥 Firebase Bağlantı Testi")
    print("="*40)
    
    try:
        # 1. Firebase Admin SDK'yı başlat
        print("1️⃣ Firebase Admin SDK başlatılıyor...")
        
        if service_account_path and os.path.exists(service_account_path):
            print(f"   📁 Service account dosyası: {service_account_path}")
            cred = credentials.Certificate(service_account_path)
            
            # Eğer zaten başlatılmışsa, yeni app oluştur
            if firebase_admin._apps:
                app = firebase_admin.initialize_app(cred, name='test_app')
                db = firestore.client(app)
            else:
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                
        else:
            print("   🔧 Default credentials kullanılıyor...")
            
            if firebase_admin._apps:
                app = firebase_admin.initialize_app(name='test_app2')
                db = firestore.client(app)
            else:
                firebase_admin.initialize_app()
                db = firestore.client()
        
        print("   ✅ Firebase Admin SDK başlatıldı")
        
        # 2. Firestore bağlantısını test et
        print("\n2️⃣ Firestore bağlantısı test ediliyor...")
        
        # Test koleksiyonu oluştur
        test_doc = {
            'test_message': 'Firebase bağlantı testi',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'test_time': datetime.now().isoformat()
        }
        
        # Test yazma
        print("   📝 Test yazma işlemi...")
        doc_ref = db.collection('connection_test').add(test_doc)
        test_doc_id = doc_ref[1].id
        print(f"   ✅ Test dokümanı oluşturuldu: {test_doc_id}")
        
        # Test okuma
        print("   📖 Test okuma işlemi...")
        doc = db.collection('connection_test').document(test_doc_id).get()
        if doc.exists:
            print("   ✅ Test dokümanı okundu")
            data = doc.to_dict()
            print(f"   📄 İçerik: {data['test_message']}")
        else:
            print("   ❌ Test dokümanı okunamadı")
            return False
        
        # 3. Test dokümanını SAKLAMA (Firebase Console'dan kontrol için)
        print("\n3️⃣ Test dokümanı saklanıyor...")
        print(f"   📋 Test dokümanı ID: {test_doc_id}")
        print("   🌐 Firebase Console'dan kontrol edebilirsiniz:")
        print("   📱 https://console.firebase.google.com")
        print("   📊 Firestore Database > connection_test koleksiyonu")
        
        # 4. Proje bilgilerini al
        print("\n4️⃣ Proje bilgileri:")
        
        # Firebase app bilgilerini al
        if firebase_admin._apps:
            app_names = list(firebase_admin._apps.keys())
            print(f"   📱 Aktif Firebase apps: {app_names}")
            
            # İlk app'in bilgilerini al
            first_app_name = app_names[0] if app_names else '[DEFAULT]'
            if first_app_name in firebase_admin._apps:
                app = firebase_admin._apps[first_app_name]
                if hasattr(app, 'project_id'):
                    print(f"   🏷️ Project ID: {app.project_id}")
        
        print("\n🎉 Firebase bağlantısı BAŞARILI!")
        print("✅ Tüm testler geçti")
        return True
        
    except Exception as e:
        print(f"\n❌ Firebase bağlantı hatası: {e}")
        print("\n🔧 Sorun giderme önerileri:")
        print("1. Service account JSON dosyasının doğru yolda olduğunu kontrol edin")
        print("2. Firebase projesinde Firestore'un etkinleştirildiğini kontrol edin")
        print("3. Service account'un Firestore izinlerine sahip olduğunu kontrol edin")
        print("4. İnternet bağlantınızı kontrol edin")
        return False

def test_with_different_methods():
    """Farklı yöntemlerle Firebase bağlantısını test et"""
    
    print("🧪 ÇOK YÖNTEMLI FIREBASE BAĞLANTI TESTİ")
    print("="*60)
    
    # Test 1: Service account dosyası ile
    print("\n🔬 Test 1: Service account dosyası ile")
    service_account_files = [
        'trendyol-firebase-service-account.json',
        'demo-firebase-service-account.json'
    ]
    
    for file_path in service_account_files:
        if os.path.exists(file_path):
            print(f"\n📁 {file_path} dosyası test ediliyor...")
            try:
                success = test_firebase_connection(file_path)
                if success:
                    print(f"✅ {file_path} ile bağlantı BAŞARILI!")
                    return True
                else:
                    print(f"❌ {file_path} ile bağlantı başarısız")
            except Exception as e:
                print(f"❌ {file_path} ile test hatası: {e}")
        else:
            print(f"⚠️ {file_path} dosyası bulunamadı")
    
    # Test 2: Environment variables ile
    print("\n🔬 Test 2: Environment variables ile")
    env_var = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if env_var:
        print(f"🌐 GOOGLE_APPLICATION_CREDENTIALS: {env_var}")
        try:
            success = test_firebase_connection()
            if success:
                print("✅ Environment variables ile bağlantı BAŞARILI!")
                return True
        except Exception as e:
            print(f"❌ Environment variables ile test hatası: {e}")
    else:
        print("⚠️ GOOGLE_APPLICATION_CREDENTIALS environment variable tanımlı değil")
    
    print("\n❌ TÜM BAĞLANTI YÖNTEMLERİ BAŞARISIZ!")
    return False

def quick_firestore_test():
    """Hızlı Firestore bağlantı testi"""
    
    print("⚡ HIZLI FIRESTORE BAĞLANTI TESTİ")
    print("="*40)
    
    try:
        # Basit bağlantı testi
        if not firebase_admin._apps:
            # Service account dosyasını bul
            if os.path.exists('trendyol-firebase-service-account.json'):
                cred = credentials.Certificate('trendyol-firebase-service-account.json')
                firebase_admin.initialize_app(cred)
                print("✅ Firebase başlatıldı")
            else:
                print("❌ Service account dosyası bulunamadı")
                return False
        
        # Firestore client oluştur
        db = firestore.client()
        
        # Basit write/read testi
        doc_ref = db.collection('test').document('connection_check')
        doc_ref.set({'status': 'connected', 'time': firestore.SERVER_TIMESTAMP})
        
        # Okunan veriyi kontrol et
        doc = doc_ref.get()
        if doc.exists:
            print("✅ Firestore okuma/yazma BAŞARILI!")
            
            # Test dokümanını SAKLAMA (Firebase Console'dan kontrol için)
            print("📋 Test verisi Firebase'de saklandı")
            print("🌐 Firebase Console'dan kontrol edebilirsiniz:")
            print("📱 https://console.firebase.google.com")
            print("📊 Firestore Database > test > connection_check")
            return True
        else:
            print("❌ Test verisi okunamadı")
            return False
            
    except Exception as e:
        print(f"❌ Hızlı test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    
    print("🔥 FIREBASE BAĞLANTI DOĞRULAMA ARACI")
    print("="*50)
    
    print("\n🔍 Hangi testi çalıştırmak istiyorsunuz?")
    print("1. ⚡ Hızlı bağlantı testi")
    print("2. 🔬 Detaylı bağlantı testi")
    print("3. 🧪 Çok yöntemli test")
    print("4. 📁 Dosya kontrolü")
    print("5. 🚪 Çıkış")
    
    choice = input("\nSeçiminiz (1-5): ").strip()
    
    if choice == '1':
        success = quick_firestore_test()
        if success:
            print("\n🎉 SONUÇ: Firebase bağlantısı çalışıyor!")
        else:
            print("\n💥 SONUÇ: Firebase bağlantısı çalışmıyor!")
    
    elif choice == '2':
        service_account = input("\nService account dosya yolu (Enter = trendyol-firebase-service-account.json): ").strip()
        if not service_account:
            service_account = 'trendyol-firebase-service-account.json'
        
        success = test_firebase_connection(service_account)
        if success:
            print("\n🎉 SONUÇ: Firebase bağlantısı çalışıyor!")
        else:
            print("\n💥 SONUÇ: Firebase bağlantısı çalışmıyor!")
    
    elif choice == '3':
        success = test_with_different_methods()
        if success:
            print("\n🎉 SONUÇ: En az bir yöntemle Firebase bağlantısı çalışıyor!")
        else:
            print("\n💥 SONUÇ: Hiçbir yöntemle Firebase bağlantısı çalışmıyor!")
    
    elif choice == '4':
        print("\n📁 DOSYA KONTROLÜ:")
        
        files_to_check = [
            'trendyol-firebase-service-account.json',
            'demo-firebase-service-account.json'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   ✅ {file_path} - {file_size} bytes")
                
                # JSON dosyasının geçerli olup olmadığını kontrol et
                try:
                    import json
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if 'project_id' in data and 'private_key' in data:
                            print(f"      📋 Project ID: {data['project_id']}")
                            print("      🔑 Private key mevcut")
                        else:
                            print("      ⚠️ Gerekli alanlar eksik")
                except Exception as e:
                    print(f"      ❌ JSON parse hatası: {e}")
            else:
                print(f"   ❌ {file_path} - Dosya bulunamadı")
        
        # Environment variable kontrolü
        env_var = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if env_var:
            print(f"\n🌐 GOOGLE_APPLICATION_CREDENTIALS: {env_var}")
            if os.path.exists(env_var):
                print("   ✅ Environment variable dosyası mevcut")
            else:
                print("   ❌ Environment variable dosyası bulunamadı")
        else:
            print("\n🌐 GOOGLE_APPLICATION_CREDENTIALS: Tanımlı değil")
    
    elif choice == '5':
        print("👋 Test aracı kapatılıyor...")
    
    else:
        print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main() 