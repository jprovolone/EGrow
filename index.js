"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.onWaterLevelUpdate = exports.onSoilMoistureUpdate = exports.onTemperatureUpdate = exports.onHumidityUpdate = void 0;
const functions = require("firebase-functions");
//const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();


//HUMIDITY
exports.onHumidityUpdate = functions.database
    .ref('/humidity')
    .onUpdate((change, context) => {
    const before = change.before.val();
    const after = change.after.val();
    if (before === after) {
        console.log("No value changed");
        return null;
    }
    else {
        const humidity = after.humidity;
        const topicName = 'EGrowSensors';
        var payload = {};
        if (before.humidity > 70 && after.humidity < 70) {
            payload = {
                notification: {
                    title: 'Humidity is now safe.',
                    body: "Humidity is at: " + humidity + "%"
                },
                apns: {
                    payload: {
                        aps: {
                            sound: 'default'
                        },
                    },
                },
                topic: topicName
            };
            return sendMessage(payload);
        }
        if (before.humidity < 40 && after.humidity > 40) {
            payload = {
                notification: {
                    title: 'Humidity is now safe.',
                    body: "Humidity is at: " + humidity + "%"
                },
                apns: {
                    payload: {
                        aps: {
                            sound: 'default'
                        },
                    },
                },
                topic: topicName
            };
            return sendMessage(payload);
        }
        if (humidity > 70) {
            // Notification details.
            payload = {
                notification: {
                    title: 'Humidity is too high!',
                    body: "Humidity is at: " + humidity + "%"
                },
                apns: {
                    payload: {
                        aps: {
                            sound: 'default'
                        },
                    },
                },
                topic: topicName
            };
            return sendMessage(payload);
        }
        if (humidity < 40) {
            payload = {
                notification: {
                    title: 'Humidity is too low!',
                    body: "Humidity is at: " + humidity + "%"
                },
                apns: {
                    payload: {
                        aps: {
                            sound: 'default'
                        },
                    },
                },
                topic: topicName
            };
            return sendMessage(payload);
        }
        else {
            return null;
        }
    }
});
//TEMPERATURE
exports.onTemperatureUpdate = functions.database
    .ref('/temperature')
    .onUpdate((change, context) => {
    const before = change.before.val();
    const after = change.after.val();
    if (before === after) {
        console.log("No value changed");
        return null;
    }
    const temperature = after.temperature;
    const topicName = 'EGrowSensors';
    if (before.temperature > 100 && after.temperature < 100) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Temperature is now safe!',
                body: "Temperature is at: " + temperature + "°F"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (before.temperature < 35 && after.temperature > 35) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Temperature is now safe!',
                body: "Temperature is at: " + temperature + "°F"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (temperature > 100) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Temperature is too high!',
                body: "Temperature is at: " + temperature + "°F"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (temperature < 35) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Temperature is too low!',
                body: "Temperature is at: " + temperature + "°F"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    else {
        return null;
    }
});
//SOIL MOISTURE
exports.onSoilMoistureUpdate = functions.database
    .ref('/soilmoisture')
    .onUpdate((change, context) => {
    const before = change.before.val();
    const after = change.after.val();
    if (before === after) {
        console.log("No value changed");
        return null;
    }
    const soilmoisture = after.soilmoisture;
    const topicName = 'EGrowSensors';
    if (before.soilmoisture < 10 && after.soilmoisture > 10) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Soil is now properly hydrated!',
                body: "Moisture is at: " + soilmoisture + "%"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (before.soilmoisture > 90 && after.soilmoisture < 90) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Soil is now properly hydrated!',
                body: "Moisture is at: " + soilmoisture + "%"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (soilmoisture < 10) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Soil is getting a little dry out here.',
                body: "Something might be wrong. Soil moisture is at: " + soilmoisture + "%"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    if (soilmoisture > 90) {
        // Notification details.
        const payload = {
            notification: {
                title: 'Soil is way too moist!',
                body: "Something might be wrong. Soil moisture is at: " + soilmoisture + "%"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    else {
        return null;
    }
});
//WATER LEVEL
exports.onWaterLevelUpdate = functions.database
    .ref('/waterlevel')
    .onUpdate((change, context) => {
    const before = change.before.val();
    const after = change.after.val();
    if (before === after) {
        console.log("No value changed");
    }
    const waterlevel = after.waterlevel;
    const topicName = 'EGrowSensors';
    if (waterlevel > 2) {
        // Notification details.
        const payload = {
            notification: {
                title: "Uh oh! Something isn't right with the water level...",
                body: "The tank might need to be manually filled"
            },
            apns: {
                payload: {
                    aps: {
                        sound: 'default'
                    },
                },
            },
            topic: topicName
        };
        return sendMessage(payload);
    }
    else {
        return null;
    }
});
//send Message Function
function sendMessage(payload) {
    // Send the message.
    return admin.messaging().send(payload)
        .then((response) => {
        console.log('Successfully sent message:', response);
    })
        .catch((error) => {
        console.error('Error sending message:', error);
    });
}
//# sourceMappingURL=index.js.map