import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: applicationWindow
    visible: true
    width: 640
    height: 480
    title: "手柄模拟"

    GridLayout {
        anchors.fill: parent
        columns: 2
        rowSpacing: 20
        columnSpacing: 20

        // 左Trigger
        Rectangle {
            id: lt
            width: 100
            height: 40
            color: "lightgreen"
            border.color: "black"
            radius: 5
        }

        // 右Trigger
        Rectangle {
            id: rt
            width: 100
            height: 40
            color: "lightgreen"
            border.color: "black"
            Layout.alignment: Qt.AlignRight
            radius: 5
        }

        // 左Bumper
        Rectangle {
            id: lb
            width: 80
            height: 40
            color: "lightgreen"
            border.color: "black"
            radius: 5
        }

        // 右Bumper
        Rectangle {
            id: rb
            width: 80
            height: 40
            color: "lightgreen"
            border.color: "black"
            Layout.alignment: Qt.AlignRight
            radius: 5
        }

        // 左摇杆
        Rectangle {
            id: lx
            width: 100
            height: 100
            color: "lightgray"
            border.color: "black"
            radius: 50

            Rectangle {
                id: lp
                width: 20
                height: 20
                color: "blue"
                radius: 10
        //                x: joystickLeftX * (parent.width - width)
        //                y: joystickLeftY * (parent.height - height)
            }
        }

        // 右按键
        GridLayout {
            rows: 3
            columns: 3
            Layout.alignment: Qt.AlignRight

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 0
                Layout.column: 1
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 1
                Layout.column: 0
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 1
                Layout.column: 2
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 2
                Layout.column: 1
            }
        }

        // 左按键 / D-pad
        GridLayout {
            rows: 3
            columns: 3

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 0
                Layout.column: 1
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 1
                Layout.column: 0
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 1
                Layout.column: 2
            }

            Rectangle {
                width: 40
                height: 40
                color: "lightblue"
                Layout.row: 2
                Layout.column: 1
            }
        }

        // 右摇杆
        Rectangle {
            width: 100
            height: 100
            color: "lightgray"
            border.color: "black"
            Layout.alignment: Qt.AlignRight
            radius: 50

            Rectangle {
                width: 20
                height: 20
                color: "blue"
                radius: 10
        //                x: joystickLeftX * (parent.width - width)
        //                y: joystickLeftY * (parent.height - height)
            }
        }

        // 空占位

        Rectangle {
            width: 10
        }
        Button {
            text: Joy.msg
        }
    }



    // 用于在Qt中处理手柄事件的接口
    QtObject {
        id: joy
    }
}
