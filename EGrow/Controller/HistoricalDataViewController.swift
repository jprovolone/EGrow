//
//  HistoricalDataViewController.swift
//  EGrow
//
//  Created by John Provost on 10/1/20.
//  Copyright © 2020 John Provost. All rights reserved.
//

import UIKit
import FirebaseFirestore
import Charts
import TinyConstraints

class HistoricalDataViewController: UIViewController, ChartViewDelegate{

    let historicalData = MainScreenViewController.historicalData
    var humidityValues = [String]()
    var temperatureValues = [String]()
    var dateValues = [String]()
    var timeValues = [String]()
    
    @IBOutlet weak var dateLabel: UILabel!
    @IBOutlet weak var humidityLabel: UILabel!
    @IBOutlet weak var temperatureLabel: UILabel!
    @IBOutlet weak var image: UIImageView!
    @IBOutlet weak var imageView: UIView!
    
    
    var humidityData = [ChartDataEntry]()
    var temperatureData = [ChartDataEntry]()
    
    @IBOutlet weak var chartView: UIView!
    
    //MARK: - Line Chart View Setup
    lazy var lineChartView: LineChartView = {
        let chartView = LineChartView()
        //chartView.backgroundColor = #colorLiteral(red: 0.2779058592, green: 0.6531479391, blue: 0.4952137798, alpha: 1)
        
        chartView.rightAxis.enabled = false
        let yAxis = chartView.leftAxis
        yAxis.labelFont = .boldSystemFont(ofSize: 12)
        yAxis.setLabelCount(6, force: false)
        yAxis.labelTextColor = #colorLiteral(red: 0.05963078886, green: 0.3969096541, blue: 0.6958708167, alpha: 1)
        yAxis.axisLineColor = .white
        
        chartView.xAxis.labelPosition = .bottom
        let xAxis = chartView.xAxis
        xAxis.labelFont = .boldSystemFont(ofSize: 12)
        xAxis.setLabelCount(0, force: true)
        xAxis.labelTextColor = #colorLiteral(red: 1.0, green: 1.0, blue: 1.0, alpha: 1.0)
        xAxis.axisLineColor = .white
        xAxis.centerAxisLabelsEnabled = false
        xAxis.drawLabelsEnabled = false
        
        chartView.animate(xAxisDuration: 1)
        
        
        return chartView
    }()
    
    //MARK: - ViewDidLoad
    override func viewDidLoad() {
        super.viewDidLoad()
        
        
        humidityLabel.adjustsFontForContentSizeCategory = true
        temperatureLabel.adjustsFontForContentSizeCategory = true
        dateLabel.adjustsFontForContentSizeCategory = true

        lineChartView.delegate = self
        view.addSubview(lineChartView)
        lineChartView.centerY(to: chartView)
        lineChartView.width(to: view)
        lineChartView.height(to: chartView)
        setChartData()
        
        self.image.layer.masksToBounds = true
        self.image.layer.cornerRadius = 7
        
        imageView.layer.cornerRadius = 7
        imageView.layer.shadowColor = UIColor.black.cgColor
        imageView.layer.shadowOpacity = 1
        imageView.layer.shadowOffset = .zero
        imageView.layer.shadowRadius = 5

        

        
        
    }
    
    //MARK: - Chart data and selection settings
    
    func setChartData() {
        getChartDataValues()
        let set1 = LineChartDataSet(entries: humidityData, label: "Humidity (%)")
        set1.mode = .cubicBezier
        set1.drawCirclesEnabled = true
        set1.circleRadius = 4
        set1.setColor(.blue)
        set1.lineWidth = 3
        set1.drawHorizontalHighlightIndicatorEnabled = false
        
        
        let set2 = LineChartDataSet(entries: temperatureData, label: "Temperature (°F)")
        set2.mode = .cubicBezier
        set2.drawCirclesEnabled = true
        set2.circleRadius = 4
        set2.setColor(.red)
        set2.lineWidth = 3
        set2.drawHorizontalHighlightIndicatorEnabled = false
        
        
        let data = LineChartData(dataSets: [set1, set2])
        data.setDrawValues(false)
        lineChartView.data = data
    }
    
    
    func getChartDataValues() {
        humidityValues = []
        temperatureValues = []
        dateValues = []
        timeValues = []
        var i = 0
        while i < historicalData.count {
            humidityValues.append(historicalData[i].humidity)
            temperatureValues.append(historicalData[i].temperature)
            dateValues.append(historicalData[i].date)
            timeValues.append(historicalData[i].time)
            i += 1
        }
        i = 0
        for humidity in humidityValues {
            let value = ChartDataEntry(x: Double(i), y: Double(humidity)!)
            humidityData.append(value)
            i += 1
        }
        i = 0
        for temperature in temperatureValues {
            let value = ChartDataEntry(x: Double(i), y: Double(temperature)!)
            temperatureData.append(value)
            i += 1
        }
    }
    
    public func chartValueSelected(_ chartView: ChartViewBase, entry: ChartDataEntry, highlight: Highlight) {
        let index = Int(entry.x)
        let date = historicalData[index].date
        let time = historicalData[index].time
        let humidity = historicalData[index].humidity
        let temperature = historicalData[index].temperature
        
        self.humidityLabel.text = "\(humidity)%"
        self.temperatureLabel.text = "\(temperature)°F"
        self.dateLabel.text = "\(date) \(time)"
    }
}
