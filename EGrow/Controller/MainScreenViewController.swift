//
//  MainScreenViewController.swift
//  EGrow
//
//  Created by John Provost on 9/11/20.
//  Copyright © 2020 John Provost. All rights reserved.
//

import UIKit
import FirebaseDatabase
import FirebaseFirestore
import UserNotifications
import Firebase

class MainScreenViewController: UIViewController {
    
    @IBOutlet weak var humidityLabel: UILabel!
    @IBOutlet weak var tempLabel: UILabel!
    @IBOutlet weak var waterLevelLabel: UILabel!
    @IBOutlet weak var soilMoistureLevel: UILabel!
    @IBOutlet weak var recentImageView: UIImageView!
    @IBOutlet weak var imageDescriptionLabel: UILabel!
    @IBOutlet weak var waterMyPlantsView: UIView!
    @IBOutlet weak var imageView: UIView!
    
    var ref: DatabaseReference!
    let db = Firestore.firestore()
    let storage = Storage.storage()
    
    static var historicalData = [SensorData]()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        
        waterMyPlantsView.layer.cornerRadius = 12
        
        imageView.layer.cornerRadius = 7
        imageView.layer.shadowColor = UIColor.black.cgColor
        imageView.layer.shadowOpacity = 1
        imageView.layer.shadowOffset = .zero
        imageView.layer.shadowRadius = 5
        
        self.tempLabel.highlightedTextColor = .cyan
        self.humidityLabel.highlightedTextColor = .cyan
        self.waterLevelLabel.highlightedTextColor = .cyan
        self.soilMoistureLevel.highlightedTextColor = .cyan
        
       // self.recentImageView.layer.masksToBounds = true
        self.recentImageView.layer.cornerRadius = 7
        
        ref = Database.database().reference()
        getFirebaseDatabase()
        getFirebaseFirestore()
        getLatestImage()
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
        
        
    }
    
    func getFirebaseDatabase() {
        ref.child("humidity").child("humidity").observe(.value) { (snapshot) in
            let humidity = snapshot.value
            self.humidityLabel.text = "\(humidity!)%"
            self.humidityLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.humidityLabel.isHighlighted = false
            }
        }
        
        ref.child("soilmoisture").child("soilmoisture").observe(.value) { (snapshot) in
            let soilmoisture = snapshot.value
            self.soilMoistureLevel.text = "\(soilmoisture!)%"
            self.soilMoistureLevel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.soilMoistureLevel.isHighlighted = false
            }
            
        }
        
        ref.child("temperature").child("temperature").observe(.value) { (snapshot) in
            let temperature = Int(round(snapshot.value as! Double))
            self.tempLabel.text = "\(temperature)°F"
            self.tempLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.tempLabel.isHighlighted = false
            }
            
        }
        
        ref.child("waterlevel").child("waterlevel").observe(.value) { (snapshot) in
            let waterlevel = snapshot.value as? Int
            
            if waterlevel == 1 {
                self.waterLevelLabel.textColor = #colorLiteral(red: 0.1764705926, green: 0.4980392158, blue: 0.7568627596, alpha: 1)
                self.waterLevelLabel.text = "OK"
            } else if waterlevel == 2 {
                self.waterLevelLabel.textColor = #colorLiteral(red: 0.8444274068, green: 0.8334051967, blue: 0.2632672191, alpha: 1)
                self.waterLevelLabel.text = "Filling"
            } else {
                self.waterLevelLabel.textColor = .red
                self.waterLevelLabel.text = "LOW"
            }
            self.waterLevelLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.waterLevelLabel.isHighlighted = false
            }
            
        }
        
    }
    
    func getFirebaseFirestore() {
        
        db.collection("historical data").addSnapshotListener { (querySnapshot, err) in
            if let err = err {
                print(err)
            } else {
                MainScreenViewController.historicalData = []
                if let snapshotDocuments = querySnapshot?.documents {
                    
                    for doc in snapshotDocuments {
                        let data = doc.data()
                        //print(data)
                        if let hDate = data["date"] as? String, let hTime = data["time"] as? String, let hTemperature =
                            data["temperature"], let hHumidity = data["humidity"] {
                            
                            //Round the temperature value because DHT11 is BULLSHIT
                            let tempFloat = (hTemperature as AnyObject).floatValue
                            let roundedTemp = String(format: "%.1f", tempFloat!)
                            
                            let sensorData = SensorData(date: hDate, humidity: "\(hHumidity)", temperature: "\(roundedTemp)", time: hTime)
                            MainScreenViewController.historicalData.append(sensorData)
                        }
                        else {
                            print("There was some stupid error")
                        }
                    }
                    self.formatTime()
                }
            }
        }
    }
    
    func formatTime() {
        let inFormatter = DateFormatter()
        inFormatter.locale = NSLocale(localeIdentifier: "en_US_POSIX") as Locale
        inFormatter.dateFormat = "HH:mm:ss"

        let outFormatter = DateFormatter()
        outFormatter.locale = NSLocale(localeIdentifier: "en_US_POSIX") as Locale
        outFormatter.dateFormat = "h:mm a"
        
        var index = 0
        while index < MainScreenViewController.historicalData.count {
            let inTime = MainScreenViewController.historicalData[index].time
            
            let date = inFormatter.date(from: inTime)!
            let outTime = outFormatter.string(from: date)
            
            MainScreenViewController.historicalData[index].time = outTime
            index += 1
        }
        
    }
    
    func getLatestImage() {
        
        // Create a reference with an initial file path and name
       // let pathReference = storage.reference(withPath: "/testing123.jpg")
        
        // Create a reference from a Google Cloud Storage URI
        let gsReference = storage.reference(forURL: "gs://egrow-20d1c.appspot.com")
        
        // Create a reference to the file you want to download
        let myImage = gsReference.child("/testing123")

        // Download in memory with a maximum allowed size of 1MB (1 * 1024 * 1024 bytes)
        myImage.getData(maxSize: 3 * 1024 * 1024) { data, error in
          if let error = error {
            print("something bad happened \(error)")
            // Uh-oh, an error occurred!
          } else {
            // Data for "images/island.jpg" is returned
            let image = UIImage(data: data!)
            self.recentImageView.image = image
          }
        }
        
        
    }
    
    
}
