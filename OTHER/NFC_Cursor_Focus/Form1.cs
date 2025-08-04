

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO.Ports;
using System.Threading;
using System.IO;

namespace ReadNFC
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        public int BaudRate;

        public byte GetDataMode;

        public byte[] RevDataBuffer = new byte[30];
        public UInt32 RevDataBufferCount;

        SerialPort Yserial = new SerialPort();

        private delegate void ProcessRxDataDelegate(); //代理

        Thread thread = null;


        string PathF = @".\MyCard.txt";
        FileStream MyCard = null;

        private void Form1_Load(object sender, EventArgs e)
        {
            SearchPort();
            switch (comboBox2.Text)
            {
                case "4800":
                    BaudRate = 4800;
                    break;
                case "7200":
                    BaudRate = 7200;
                    break;
                case "9600":
                    BaudRate = 9600;
                    break;
                case "14400":
                    BaudRate = 14400;
                    break;
                case "19200":
                    BaudRate = 19200;
                    break;
                case "38400":
                    BaudRate = 38400;
                    break;
                case "57600":
                    BaudRate = 57600;
                    break;
                case "115200":
                    BaudRate = 115200;
                    break;
                default:
                    BaudRate = 9600;
                    break;
            }
            //创建文件
            if (File.Exists(PathF) == false) 
            {
              MyCard = File.Create(PathF);
              MyCard.Close();
            }
            //else
            //{
            //  MyCard = File.OpenWrite(PathF);
            //}
        }
        private static void AddText(FileStream fs, string value)
        {
          byte[] info = new UTF8Encoding(true).GetBytes(value);
          fs.Write(info, 0, info.Length);
        }

        public void SearchPort()
        {
            string[] ports = SerialPort.GetPortNames();

            foreach (string port in ports)
            {
                comboBox1.Items.Add(port);
            }

            if (ports.Length > 0)
            {
                comboBox1.Text = ports[0];//comboBox1.Items[0].ToString();
                //comboBox1.Items.Remove(3);
            }
            else
            {
                MessageBox.Show("没有发现可用端口");
            }
        }
        private void button2_Click(object sender, EventArgs e)
        {
          if (comboBox1.Items.Count != 0)
          {
              try
              {
                if (button2.Text == "开启运行")
                {
                  if (Yserial.IsOpen == false)
                  {
                    Yserial.PortName = comboBox1.Text;
                    Yserial.BaudRate = BaudRate;
                    Yserial.Open();
                    button2.Text = "停止运行";
                    comboBox1.Enabled = false;
                    comboBox2.Enabled = false;
                    //MyCard = File.OpenWrite(PathF);
                    //AddText(MyCard, "This is some text");
                    //MyCard.Close();
                    //File.c
                    thread = new Thread(RevData);
                    thread.IsBackground = true;
                    thread.Start();
                  }
                }
                else
                {
                  if (Yserial.IsOpen)
                  {
                    Yserial.Close();
                  }
                  button2.Text = "开启运行";
                  comboBox1.Enabled = true;
                  comboBox2.Enabled = true;
                  if (thread.ThreadState == ThreadState.Aborted)
                  {
                    thread.Abort();
                  }
                }
              }
              catch//InvalidOperationException w
              {
                  MessageBox.Show("   端口被占用\n请选择正确的端口", "错误");
                  //thread.Abort();
              }
          }
          else
          {
              MessageBox.Show("请选择正确的端口", "错误");
          }
        }
        private void comboBox2_SelectedIndexChanged(object sender, EventArgs e)
        {
            switch (comboBox2.Text)
            {
                case "4800":
                    BaudRate = 4800;
                    break;
                case "7200":
                    BaudRate = 7200;
                    break;
                case "9600":
                    BaudRate = 9600;
                    break;
                case "14400":
                    BaudRate = 14400;
                    break;
                case "19200":
                    BaudRate = 19200;
                    break;
                case "38400":
                    BaudRate = 38400;
                    break;
                case "57600":
                    BaudRate = 57600;
                    break;
                case "115200":
                    BaudRate = 115200;
                    break;
                default:
                    BaudRate = 9600;
                    break;

            }
        }
        private void Form1Close(object sender, FormClosedEventArgs e)
        {
          if (Yserial.IsOpen)
          {
            Yserial.Close();
          }
          this.Dispose();//关闭程序释放资源
        }
        public void CheckSum(byte[] buf, byte len)
        {
            byte i;
            byte checksum;
            checksum = 0;
            for (i = 0; i < (len - 1); i++)
            {
                checksum ^= buf[i];
            }
            buf[len - 1] = (byte)~checksum;
        }
        public string byteToHexStr(byte[] bytes, int len)  //数组转十六进制字符显示
        {
            string returnStr = "";
            if (bytes != null)
            {
                for (int i = 0; i < len; i++)
                {
                    returnStr += bytes[i].ToString("X2");
                }
            }
            return returnStr;
        }
        public string byteToHexStrH(byte[] bytes, int len)  //数组转十六进制字符显示
        {
          string returnStr = "";
          if (bytes != null)
          {
            for (int i = 0; i < len; i++)
            {
              returnStr += bytes[i].ToString("X2");
              returnStr += ' ';
            }
          }
          return returnStr;
        }
        private static byte[] strToToHexByte(string hexString) //字符串转16进制
        {
            //hexString = hexString.Replace(" ", " "); 
            if ((hexString.Length % 2) != 0)
                hexString = "0" + hexString;
            byte[] returnBytes = new byte[hexString.Length / 2];
            for (int i = 0; i < returnBytes.Length; i++)
                returnBytes[i] = Convert.ToByte(hexString.Substring(i * 2, 2), 16);
            return returnBytes;
        }
        private static byte[] strToDecByte(string hexString)//字符串转10进制
        {
          //hexString = hexString.Replace(" ", " "); 
          if ((hexString.Length % 2) != 0)
            hexString = "0" + hexString;
          byte[] returnBytes = new byte[hexString.Length / 2];
          for (int i = 0; i < returnBytes.Length; i++)
            returnBytes[i] = Convert.ToByte(hexString.Substring(i * 2, 2), 10);
          return returnBytes;
        }
        public static bool CheckSumOut(byte[] buf, byte len)
        {
          byte i;
          byte checksum;
          checksum = 0;
          for (i = 0; i < (len - 1); i++)
          {
            checksum ^= buf[i];
          }
          if (buf[len - 1] == (byte)~checksum)
          {
            return true;
          }
          return false;
        }
        
        public void RevData()
        {
            while (Yserial.IsOpen == true)
            {
                System.Threading.Thread.Sleep(10);
                try
                {
                    ProcessRxDataDelegate fc = new ProcessRxDataDelegate(AsyRevData);
                    this.Invoke(fc);
                }
                catch
                {
                   ;
                }
            }
        }
        public void AsyRevData()
        {

          int revbuflen;

          byte pkttype;
          byte pktlength = 0x0;
          byte cmd;
          byte err;

          string carddata;

          bool revflag;
          bool status;


          byte[] rdatacopy = new byte[30];

          try
          {
            if (Yserial.IsOpen)
            {
              revbuflen = Yserial.BytesToRead;
              revflag = false;
              if (revbuflen > 0)
              {
                revflag = true;
                System.Threading.Thread.Sleep(50);
              }
              RevDataBufferCount = 0;
              while (revflag)
              {
                RevDataBuffer[RevDataBufferCount] = (byte)Yserial.ReadByte();
                RevDataBufferCount = RevDataBufferCount + 1;
                if (RevDataBufferCount >= 30)//防止缓冲区溢出
                {
                  RevDataBufferCount = 0;
                }
                System.Threading.Thread.Sleep(2);
                revbuflen = Yserial.BytesToRead;
                if (revbuflen > 0)
                {
                  revflag = true;
                }
                else
                {
                  revflag = false;
                }
              }
              if ((RevDataBuffer[1] <= RevDataBufferCount) && (RevDataBufferCount != 0x0))
              {
                RevDataBufferCount = 0x0;
                status = CheckSumOut(RevDataBuffer, RevDataBuffer[1]);//计算校验和
                if (status == false)
                {
                  return;
                }

                textBox2.Text = byteToHexStrH(RevDataBuffer, RevDataBuffer[1]);

                pkttype = RevDataBuffer[0];  //获取包类型
                pktlength = RevDataBuffer[1]; //获取包长度
                cmd = RevDataBuffer[2]; //获取命令
                err = RevDataBuffer[4];

                if (err != 0)
                {
                  return;
                }
                for (int i = 0; i < pktlength - 5; i++)
                {
                  RevDataBuffer[i] = RevDataBuffer[i + 5]; //获取数据
                }
                if (pkttype == 0x04)
                {
                  carddata = "00000000";
                  switch (cmd)
                  { 
                    case 0x02:
                      carddata = byteToHexStr(RevDataBuffer, pktlength - 6);
                      status = true;
                      break;
                    case 0x03:
                      carddata = byteToHexStr(RevDataBuffer, pktlength - 6);
                      status = true;
                      break;
                    case 0x04:
                      carddata = byteToHexStr(RevDataBuffer, pktlength - 6); 
                      status = true;
                      break;
                    default:
                      status = false;
                      break;
                  }
                  if (status == true)
                  {
                    MyCard = File.OpenWrite(PathF);
                    AddText(MyCard, "5555\r\n");
                    AddText(MyCard, carddata);
                    MyCard.Close();
                    System.Windows.Forms.SendKeys.Send(carddata); 
                  }
                }
              }
            }
            else
            {
              button2.Text = "开启运行";
              comboBox1.Enabled = true;
              comboBox2.Enabled = true;
              if (thread.ThreadState != ThreadState.Aborted)
              {
                thread.Abort();
              }
            }
          }
          catch
          {
            button2.Text = "开启运行";
            comboBox1.Enabled = true;
            comboBox2.Enabled = true;
            if (Yserial.IsOpen)
            {
              Yserial.Close();
            }
            if (thread.ThreadState != ThreadState.Aborted)
            {
              thread.Abort();
            }
          }
       }
   }
}
