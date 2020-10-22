//
//  historicalDataDecoder.swift
//  EGrow
//
//  Created by John Provost on 10/12/20.
//  Copyright © 2020 John Provost. All rights reserved.
//

import Foundation
import UIKit


struct SensorData: Codable {
    
    var date: String
    var humidity: String
    var temperature: String
    var time: String
    
}
