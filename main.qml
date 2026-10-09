import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

ApplicationWindow {
    id: root
    visible: true
    width: 800
    height: 500
    title: "手柄输入法"
    color: "#2b2b2b"

    // 配色
    property color bgColor: "#2b2b2b"
    property color panelColor: "#3c3c3c"
    property color accentBlue: "#4fc3f7"
    property color accentRed: "#ef5350"
    property color textLight: "#e0e0e0"
    property color textDim: "#808080"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        // 顶部状态栏
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Label {
                text: "🎮 手柄输入法"
                font.pixelSize: 18
                font.bold: true
                color: textLight
            }

            Item { Layout.fillWidth: true }

            // 连接状态指示
            Rectangle {
                width: 12; height: 12
                radius: 6
                color: (Joy.lx !== 0 || Joy.ly !== 0 || Joy.rx !== 0 || Joy.ry !== 0)
                       ? "#4caf50" : "#ff9800"
            }
            Label {
                text: (Joy.lx !== 0 || Joy.ly !== 0 || Joy.rx !== 0 || Joy.ry !== 0)
                      ? "已连接" : "等待连接"
                color: textDim
                font.pixelSize: 13
            }
        }

        // 主体：左右手柄面板
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 24

            // ── 左面板 ──
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 8
                color: panelColor
                border.color: accentBlue
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Label {
                        text: "左侧"
                        font.pixelSize: 14
                        font.bold: true
                        color: accentBlue
                    }

                    // 左摇杆可视化
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: Math.min(width, height) / 2
                        color: "transparent"
                        border.color: accentBlue
                        border.width: 2
                        opacity: 0.4

                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width; height: 1
                            color: accentBlue; opacity: 0.3
                        }
                        Rectangle {
                            anchors.centerIn: parent
                            width: 1; height: parent.height
                            color: accentBlue; opacity: 0.3
                        }

                        Rectangle {
                            width: 16; height: 16; radius: 8
                            color: accentBlue
                            x: parent.width / 2 + Joy.lx * (parent.width / 2 - 8)
                            y: parent.height / 2 + Joy.ly * (parent.height / 2 - 8)
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Rectangle {
                            width: 60; height: 32; radius: 4
                            color: Joy.lt ? accentBlue : "transparent"
                            border.color: Joy.lt ? accentBlue : textDim; border.width: 1
                            Label { anchors.centerIn: parent; text: "LT"; font.bold: true
                                    color: Joy.lt ? bgColor : textLight; font.pixelSize: 12 }
                        }
                        Item { Layout.fillWidth: true }
                        Rectangle {
                            width: 60; height: 32; radius: 4
                            color: Joy.buttons[4] ? accentBlue : "transparent"
                            border.color: Joy.buttons[4] ? accentBlue : textDim; border.width: 1
                            Label { anchors.centerIn: parent; text: "LB"; font.bold: true
                                    color: Joy.buttons[4] ? bgColor : textLight; font.pixelSize: 12 }
                        }
                    }
                }
            }

            // ── 右面板 ──
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 8
                color: panelColor
                border.color: accentRed
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Label {
                        text: "右侧"
                        font.pixelSize: 14
                        font.bold: true
                        color: accentRed
                    }

                    // 右摇杆可视化
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: Math.min(width, height) / 2
                        color: "transparent"
                        border.color: accentRed
                        border.width: 2
                        opacity: 0.4

                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width; height: 1
                            color: accentRed; opacity: 0.3
                        }
                        Rectangle {
                            anchors.centerIn: parent
                            width: 1; height: parent.height
                            color: accentRed; opacity: 0.3
                        }

                        Rectangle {
                            width: 16; height: 16; radius: 8
                            color: accentRed
                            x: parent.width / 2 + Joy.rx * (parent.width / 2 - 8)
                            y: parent.height / 2 + Joy.ry * (parent.height / 2 - 8)
                        }
                    }

                    // 右侧 ABXY 按钮
                    GridLayout {
                        Layout.alignment: Qt.AlignHCenter
                        rows: 3; columns: 3
                        rowSpacing: 4; columnSpacing: 4

                        Item { width: 44; height: 44 }
                        Rectangle { width: 44; height: 44; radius: 22
                            color: Joy.buttons[3] ? accentRed : "transparent"
                            border.color: Joy.buttons[3] ? accentRed : textDim; border.width: 2
                            Label { anchors.centerIn: parent; text: "Y"; font.bold: true
                                    color: Joy.buttons[3] ? "#fff" : textDim; font.pixelSize: 14 }
                        }
                        Item { width: 44; height: 44 }

                        Rectangle { width: 44; height: 44; radius: 22
                            color: Joy.buttons[2] ? accentRed : "transparent"
                            border.color: Joy.buttons[2] ? accentRed : textDim; border.width: 2
                            Label { anchors.centerIn: parent; text: "X"; font.bold: true
                                    color: Joy.buttons[2] ? "#fff" : textDim; font.pixelSize: 14 }
                        }
                        Item { width: 44; height: 44 }
                        Rectangle { width: 44; height: 44; radius: 22
                            color: Joy.buttons[1] ? accentRed : "transparent"
                            border.color: Joy.buttons[1] ? accentRed : textDim; border.width: 2
                            Label { anchors.centerIn: parent; text: "B"; font.bold: true
                                    color: Joy.buttons[1] ? "#fff" : textDim; font.pixelSize: 14 }
                        }

                        Item { width: 44; height: 44 }
                        Rectangle { width: 44; height: 44; radius: 22
                            color: Joy.buttons[0] ? accentRed : "transparent"
                            border.color: Joy.buttons[0] ? accentRed : textDim; border.width: 2
                            Label { anchors.centerIn: parent; text: "A"; font.bold: true
                                    color: Joy.buttons[0] ? "#fff" : textDim; font.pixelSize: 14 }
                        }
                        Item { width: 44; height: 44 }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Rectangle {
                            width: 60; height: 32; radius: 4
                            color: Joy.buttons[5] ? accentRed : "transparent"
                            border.color: Joy.buttons[5] ? accentRed : textDim; border.width: 1
                            Label { anchors.centerIn: parent; text: "RB"; font.bold: true
                                    color: Joy.buttons[5] ? bgColor : textLight; font.pixelSize: 12 }
                        }
                        Item { Layout.fillWidth: true }
                        Rectangle {
                            width: 60; height: 32; radius: 4
                            color: Joy.rt ? accentRed : "transparent"
                            border.color: Joy.rt ? accentRed : textDim; border.width: 1
                            Label { anchors.centerIn: parent; text: "RT"; font.bold: true
                                    color: Joy.rt ? bgColor : textLight; font.pixelSize: 12 }
                        }
                    }
                }
            }
        }

        // 底部：轴值读数
        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            Label { text: "LX: " + Joy.lx.toFixed(2); font.pixelSize: 12; font.family: "Consolas"
                    color: Math.abs(Joy.lx) > 0.15 ? accentBlue : textDim }
            Label { text: "LY: " + Joy.ly.toFixed(2); font.pixelSize: 12; font.family: "Consolas"
                    color: Math.abs(Joy.ly) > 0.15 ? accentBlue : textDim }
            Item { Layout.fillWidth: true }
            Label { text: "RX: " + Joy.rx.toFixed(2); font.pixelSize: 12; font.family: "Consolas"
                    color: Math.abs(Joy.rx) > 0.15 ? accentRed : textDim }
            Label { text: "RY: " + Joy.ry.toFixed(2); font.pixelSize: 12; font.family: "Consolas"
                    color: Math.abs(Joy.ry) > 0.15 ? accentRed : textDim }
        }
    }
}
