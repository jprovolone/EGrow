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

class MainScreenViewController: UIViewController {
    
    @IBOutlet weak var humidityLabel: UILabel!
    @IBOutlet weak var tempLabel: UILabel!
    @IBOutlet weak var waterLevelLabel: UILabel!
    @IBOutlet weak var soilMoistureLevel: UILabel!
    @IBOutlet weak var recentImageView: UIImageView!
    @IBOutlet weak var imageDescriptionLabel: UILabel!
    
    var ref: DatabaseReference!
    let db = Firestore.firestore()
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.tempLabel.highlightedTextColor = .cyan
        self.humidityLabel.highlightedTextColor = .cyan
        self.waterLevelLabel.highlightedTextColor = .cyan
        self.soilMoistureLevel.highlightedTextColor = .cyan
        
        self.recentImageView.layer.masksToBounds = true
        self.recentImageView.layer.cornerRadius = 7
        
        ref = Database.database().reference()
        getFirebaseDatabase()
        
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
        
    }
    
    func getFirebaseDatabase() {
        ref.child("humidity").observe(.value) { (snapshot) in
            let humidity = snapshot.value
            self.humidityLabel.text = "\(humidity!)%"
            self.humidityLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.humidityLabel.isHighlighted = false
            }
        }
        
        ref.child("soilmoisture").observe(.value) { (snapshot) in
            let soilmoisture = snapshot.value
            self.soilMoistureLevel.text = "\(soilmoisture!)%"
            self.soilMoistureLevel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.soilMoistureLevel.isHighlighted = false
            }

        }
        
        ref.child("temperature").observe(.value) { (snapshot) in
            let temperature = Int(round(snapshot.value as! Double))
            self.tempLabel.text = "\(temperature)°F"
            self.tempLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.tempLabel.isHighlighted = false
            }

        }
        
        ref.child("waterlevel").observe(.value) { (snapshot) in
            let waterlevel = snapshot.value as? Int
            
            if waterlevel == 1 {
                self.waterLevelLabel.textColor = #colorLiteral(red: 0.5843137503, green: 0.8235294223, blue: 0.4196078479, alpha: 1)
                self.waterLevelLabel.text = "OK"
            } else if waterlevel == 2 {
                self.waterLevelLabel.textColor = .yellow
                self.waterLevelLabel.text = "Filling"
            } else {
                self.waterLevelLabel.textColor = .red
                self.waterLevelLabel.text = "LOW"
//                let content = UNMutableNotificationContent()
//                content.title = "Uh oh! Water level is low!"
//                content.body = "The water level appears to be low! Make sure the hose is still connected so EGrow can grow your plants!"
//
//                // Configure the date
//                let date = NSDate()
//                let calendar = NSCalendar.current
//                let components = calendar.dateComponents(<#T##components: Set<Calendar.Component>##Set<Calendar.Component>#>, from: <#T##Date#>)
//                let hour = components.hour
//                let minutes = components.minute
//
//                var dateComponents = DateComponents()
//                dateComponents.calendar = Calendar.current
//
//                dateComponents.hour = hour
//                dateComponents.minute = minutes
//
//
//                // Create the trigger as a repeating event.
//                let trigger = UNCalendarNotificationTrigger(
//                         dateMatching: dateComponents, repeats: false)
//
//                // Create the request
//                let uuidString = UUID().uuidString
//                let request = UNNotificationRequest(identifier: uuidString,
//                            content: content, trigger: trigger)
//
//                // Schedule the request with the system.
//                let notificationCenter = UNUserNotificationCenter.current()
//                notificationCenter.add(request) { (error) in
//                   if error != nil {
//                      print("There was an error scheduling notification")
//                   }
//                }

            }
            
            self.waterLevelLabel.isHighlighted = true
            Timer.scheduledTimer(withTimeInterval: 1, repeats: false) { (Timer) in
                self.waterLevelLabel.isHighlighted = false
            }

        }
        
    }
    
    
    
}
