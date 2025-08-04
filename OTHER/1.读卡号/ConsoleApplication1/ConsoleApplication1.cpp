// ConsoleApplication1.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"  
#include "SerialPort.h"
#include <process.h>  
#include <iostream>

using namespace std;

UCHAR  CmdReadId[8] = { 0x01, 0x08, 0xA1, 0x20, 0x00, 0x01, 0x00, 0x76 };

void CheckSumOut(UCHAR *buf, UCHAR len)
{
	UCHAR i;
	UCHAR checksum;
	checksum = 0;
	for (i = 0; i < (len - 1); i++)
	{
		checksum ^= buf[i];
	}
	buf[len - 1] = (UCHAR)~checksum;
}

bool CheckSumIn(UCHAR *buf, UCHAR len)
{
	UCHAR i;
	UCHAR checksum;
	checksum = 0;
	for (i = 0; i < (len - 1); i++)
	{
		checksum ^= buf[i];
	}
	if (buf[len - 1] == (UCHAR)~checksum)
	{
		return true;
	}
	return false;
}

//字节流转换为十六进制字符串的另一种实现方式  
void Hex2Str(const UCHAR *sSrc, UCHAR *sDest, int nSrcLen)
{
	int  i;
	char szTmp[3];

	for (i = 0; i < nSrcLen; i++)
	{
		sprintf_s(szTmp, "%02X", (unsigned char)sSrc[i]);
		memcpy(&sDest[i * 2], szTmp, 2);
	}
	sDest[nSrcLen * 2 ] = '\0';
	return;
}
int main(int argc, _TCHAR* argv[])
{
	UCHAR inbyte;
	UCHAR revdata[32];
	UINT len = 0;
	UINT readbytes;
	UINT i;

	SerialPort mySerialPort;

	if (!mySerialPort.InitPort(9)) //初始化COM9，并打开COM9
	{
		cout << "初始化COM9失败，请检查读写器端口是否为COM9，或者是否被其它软件打开占用！" << endl;
		cout << "按任意键后，回车退出程序！" << endl;
		cin >> inbyte;
	}
	else
	{
		cout << "初始化COM3成功!" << endl;
		cout << "请将IC卡放读写器感应区内，输入数字'0'按回车开始读卡……\n" << endl;;
		while (true)
		{
			std::cin >> inbyte;
			if (inbyte == '0')
			{
				cout << "读卡号开始……" << endl;;
				mySerialPort.WriteData(CmdReadId, CmdReadId[1]);
				Sleep(200); // 延时200毫秒等待读写器返回数据，延时太小可能无法接收完整的数据包
				len = mySerialPort.GetBytesInCOM(); //获取串口缓冲区中字节数
				if (len >= 8) // 读卡号读卡器返回的数据包长度：失败为8字节，成功为12字节
				{
					readbytes = 0;
					do // 获取串口缓冲区数据
					{
						inbyte = 0;
						if (mySerialPort.ReadChar(inbyte) == true)
						{
							revdata[readbytes] = inbyte;
							readbytes++;
						}
					} while (--len);
					if ((revdata[0] = 0x01) && ((revdata[1] == 8) || (revdata[1] == 12)) && (revdata[1] == readbytes) && (revdata[2] == 0x0A1) && (revdata[3] = 0x20))
					{
						bool status = CheckSumIn(revdata, revdata[1]);
						if (status)
						{
							if (revdata[4] == 0x00)
							{
								UCHAR cardtype[5]; //保存卡类型
								UCHAR id[9]; //保存卡号
								Hex2Str(&revdata[5], &cardtype[0], 2); // 数组revdata[5]开始2字节为卡类型
								Hex2Str(&revdata[7], &id[0], 4); // 数组revdata[7]开始4字节为卡号
								cout << "读卡号成功，卡类型:" << cardtype <<"，卡号："<<id << endl;
							}
							else
							{
								cout << "读卡号失败，没有检测到卡……，请检查IC卡是否放置在读卡器的感应区内！" << endl;
							}
						}
					}
				}
				else
				{
					cout << "读卡号超时……，请检查读卡器的连接是否正常！" << endl;
					while (len > 0)
					{
						mySerialPort.ReadChar(inbyte);
					}
				}
			}
		}
	}
}

