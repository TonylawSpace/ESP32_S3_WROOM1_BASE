// ConsoleApplication1.cpp : �������̨Ӧ�ó������ڵ㡣
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

//�ֽ���ת��Ϊʮ�������ַ�������һ��ʵ�ַ�ʽ  
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

	if (!mySerialPort.InitPort(9)) //��ʼ��COM9������COM9
	{
		cout << "��ʼ��COM9ʧ�ܣ������д���˿��Ƿ�ΪCOM9�������Ƿ����������ռ�ã�" << endl;
		cout << "��������󣬻س��˳�����" << endl;
		cin >> inbyte;
	}
	else
	{
		cout << "��ʼ��COM3�ɹ�!" << endl;
		cout << "�뽫IC���Ŷ�д����Ӧ���ڣ���������'0'���س���ʼ��������\n" << endl;;
		while (true)
		{
			std::cin >> inbyte;
			if (inbyte == '0')
			{
				cout << "�����ſ�ʼ����" << endl;;
				mySerialPort.WriteData(CmdReadId, CmdReadId[1]);
				Sleep(200); // ��ʱ200����ȴ���д���������ݣ���ʱ̫С�����޷��������������ݰ�
				len = mySerialPort.GetBytesInCOM(); //��ȡ���ڻ��������ֽ���
				if (len >= 8) // �����Ŷ��������ص����ݰ����ȣ�ʧ��Ϊ8�ֽڣ��ɹ�Ϊ12�ֽ�
				{
					readbytes = 0;
					do // ��ȡ���ڻ���������
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
								UCHAR cardtype[5]; //���濨����
								UCHAR id[9]; //���濨��
								Hex2Str(&revdata[5], &cardtype[0], 2); // ����revdata[5]��ʼ2�ֽ�Ϊ������
								Hex2Str(&revdata[7], &id[0], 4); // ����revdata[7]��ʼ4�ֽ�Ϊ����
								cout << "�����ųɹ���������:" << cardtype <<"�����ţ�"<<id << endl;
							}
							else
							{
								cout << "������ʧ�ܣ�û�м�⵽������������IC���Ƿ�����ڶ������ĸ�Ӧ���ڣ�" << endl;
							}
						}
					}
				}
				else
				{
					cout << "�����ų�ʱ����������������������Ƿ�������" << endl;
					while (len > 0)
					{
						mySerialPort.ReadChar(inbyte);
					}
				}
			}
		}
	}
}

