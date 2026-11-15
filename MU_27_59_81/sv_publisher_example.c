/*
 * sv_publisher_example.c
 *
 * Example program for Sampled Values (SV) publisher
 */

#include "goose_receiver.h"
#include "goose_subscriber.h"
#include "iec61850_server.h"
#include "sv_publisher.h"
#include "hal_thread.h"
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>

#define _USE_MATH_DEFINES
#include <math.h>

/* Include the generated header with the model access handles */
#include "static_model.h"

/* import IEC 61850 device model created from SCL-File */
extern IedModel iedModel;
static IedServer iedServer = NULL;

static int running = 0;
static int svcbEnabled = 1;

static bool running = true;

void sigint_handler(int signalId)
{
    running = 0;
}

static int amp1;
static int amp2;
static int amp3;
static int amp4;

static int amp1q;
static int amp2q;
static int amp3q;
static int amp4q;

static int vol1;
static int vol2;
static int vol3;
static int vol4;

static int vol1q;
static int vol2q;
static int vol3q;
static int vol4q;

static SVPublisher svPublisher;
static SVPublisher_ASDU asdu;

static float vol10,vol20,vol30;
static float amp10,amp20,amp30;
static float an[6];

static void
setupSVPublisher(const char* svInterface)
{
    svPublisher = SVPublisher_create(NULL, svInterface);

    if (svPublisher) {

        asdu = SVPublisher_addASDU(svPublisher, "VMU01", NULL, 1);

        amp1 = SVPublisher_ASDU_addINT32(asdu);
        amp1q = SVPublisher_ASDU_addQuality(asdu);
        amp2 = SVPublisher_ASDU_addINT32(asdu);
        amp2q = SVPublisher_ASDU_addQuality(asdu);
        amp3 = SVPublisher_ASDU_addINT32(asdu);
        amp3q = SVPublisher_ASDU_addQuality(asdu);
        amp4 = SVPublisher_ASDU_addINT32(asdu);
        amp4q = SVPublisher_ASDU_addQuality(asdu);

        vol1 = SVPublisher_ASDU_addINT32(asdu);
        vol1q = SVPublisher_ASDU_addQuality(asdu);
        vol2 = SVPublisher_ASDU_addINT32(asdu);
        vol2q = SVPublisher_ASDU_addQuality(asdu);
        vol3 = SVPublisher_ASDU_addINT32(asdu);
        vol3q = SVPublisher_ASDU_addQuality(asdu);
        vol4 = SVPublisher_ASDU_addINT32(asdu);
        vol4q = SVPublisher_ASDU_addQuality(asdu);

        SVPublisher_ASDU_setSmpCntWrap(asdu, 4800);
        SVPublisher_ASDU_setRefrTm(asdu, 0);

        SVPublisher_setupComplete(svPublisher);
    }
}

static void sVCBEventHandler (SVControlBlock* svcb, int event, void* parameter)
{
    if (event == IEC61850_SVCB_EVENT_ENABLE)
        svcbEnabled = 1;
    else if (event == IEC61850_SVCB_EVENT_DISABLE)
        svcbEnabled = 0;
}

static void
goCbEventHandler(MmsGooseControlBlock goCb, int event, void* parameter)
{
    printf("Access to GoCB: %s\n", MmsGooseControlBlock_getName(goCb));
    printf("         GoEna: %i\n", MmsGooseControlBlock_getGoEna(goCb));
}

static void
gooseListener(GooseSubscriber subscriber, void* parameter)
{
    MmsValue* values = GooseSubscriber_getDataSetValues(subscriber);

    char buffer[50];

    MmsValue_printToBuffer(values, buffer, 50);


    char b; char c; char d;

    b = buffer[1];
    c = buffer[7];
    d = buffer[11];
    uint64_t y = Hal_getTimeInMs();

    //printf("\n%d\n%d\n", b, c);

    if(b == 116){
        IedServer_updateBooleanAttributeValue(iedServer, IEDMODEL_BinIO_BinaryInputs_LPDI3_In_stVal, true);
        FILE *file;
        file = fopen("AjustesMU.txt","r");
        fscanf(file,"%f\n",&amp10);
        fscanf(file,"%f\n",&an[0]);
        fscanf(file,"%f\n",&amp20);
        fscanf(file,"%f\n",&an[1]);
        fscanf(file,"%f\n",&amp30);
        fscanf(file,"%f\n",&an[2]);
        fscanf(file,"%f\n",&vol10);
        fscanf(file,"%f\n",&an[3]);
        fscanf(file,"%f\n",&vol20);
        fscanf(file,"%f\n",&an[4]);
        fscanf(file,"%f\n",&vol30);
        fscanf(file,"%f\n",&an[5]);
        fclose(file);
    }
    
    if(c == 116){
        IedServer_updateBooleanAttributeValue(iedServer, IEDMODEL_BinIO_BinaryInputs_LPDI3_In_stVal, false);
        amp10 = 0;
        amp20 = 0;
        amp30 = 0;
        vol10 = 0;
        vol20 = 0;
        vol30 = 0;
        an[0] = 0;
        an[1] = 0;
        an[2] = 0;
        an[3] = 0;
        an[4] = 0;
        an[5] = 0;
    }
    /*
    printf("-------------------------------------------------------------------------------------------------------------\n");            
    printf("                               PRIMEIRA MENSAGEM GOOSE ASSINADA VIED 1                                       \n");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    */
}

int
main(int argc, char** argv)
{
    float r_transformacao = 2.8868;
    char* interface;
  
    if (argc > 1)
        interface = argv[1];
    else
        interface = "eth1";
  
    printf("Using interface %s\n", interface);

    signal(SIGINT, sigint_handler);

    SVPublisher svPublisher = SVPublisher_create(NULL, interface);

    FILE *file;
    file = fopen("AjustesMU.txt","r");
    fscanf(file,"%f\n",&amp10);
    fscanf(file,"%f\n",&an[0]);
    fscanf(file,"%f\n",&amp20);
    fscanf(file,"%f\n",&an[1]);
    fscanf(file,"%f\n",&amp30);
    fscanf(file,"%f\n",&an[2]);
    fscanf(file,"%f\n",&vol10);
    fscanf(file,"%f\n",&an[3]);
    fscanf(file,"%f\n",&vol20);
    fscanf(file,"%f\n",&an[4]);
    fscanf(file,"%f\n",&vol30);
    fscanf(file,"%f\n",&an[5]);
    fclose(file);

    int voltageA;
    int voltageB;
    int voltageC;
    int voltageN;
    int currentA;
    int currentB;
    int currentC;
    int currentN;

    if (svPublisher) {

        /* Create first ASDU and add data points */

        SVPublisher_ASDU asdu1 = SVPublisher_addASDU(svPublisher, "IEDNameMU0101", NULL, 1);

        int float1 = SVPublisher_ASDU_addINT64(asdu1);
        int float2 = SVPublisher_ASDU_addINT64(asdu1);
        int float3 = SVPublisher_ASDU_addINT64(asdu1);
        int float7 = SVPublisher_ASDU_addINT64(asdu1);
        int float4 = SVPublisher_ASDU_addINT64(asdu1);
        int float5 = SVPublisher_ASDU_addINT64(asdu1);
        int float6 = SVPublisher_ASDU_addINT64(asdu1);
        int float8 = SVPublisher_ASDU_addINT64(asdu1);
        
        int ts1 = SVPublisher_ASDU_addTimestamp(asdu1);

        SVPublisher_setupComplete(svPublisher);

        float fVal1 = 0;
        float fVal2 = 0;
        float fVal3 = 0;
        float fVal4 = 0;
        float fVal5 = 0;
        float fVal6 = 0;
        float fVal7 = 0;
        float fVal8 = 0;
        float freq = 60.00;
        float vpico = 1697.06;//falta com BF
        //float vpico = 1272.8;//falta sem BF
        //float vpico = 800;//pré-falta
        float tpico = 97580.7358;
        float tempo;
        double x;

        while (running) {
            Timestamp ts;
            Timestamp_clearFlags(&ts);
            Timestamp_setTimeInMilliseconds(&ts, Hal_getTimeInMs());

            x = 2*M_PI*freq*tempo;
            tempo = (tempo + 0.0002083);

            fVal1 = vpico*sin(x)*1000;
            fVal2 = vpico*sin(x + 4.18879)*1000;
            fVal3 = vpico*sin(x + 2.0944)*1000; 
            fVal4 = tpico*sin(x)*100;
            fVal5 = tpico*sin(x+4.18879)*100;
            fVal6 = tpico*sin(x+2.0944)*100;
            fVal7 = vpico*sin(x)*1000;
            fVal8 = tpico*sin(x)*100;

            /*
            IedServer_lockDataModel(iedServer);

            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_I01ATCTR1_AmpSv_instMag_i, currentA);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_I01ATCTR1_AmpSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_I01BTCTR2_AmpSv_instMag_i, currentA);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_I01BTCTR2_AmpSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_I01CTCTR3_AmpSv_instMag_i, currentA);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_I01CTCTR3_AmpSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_I01NTCTR4_AmpSv_instMag_i, currentA);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_I01NTCTR4_AmpSv_q, q);

            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_U01ATVTR1_VolSv_instMag_i, voltageA);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_U01ATVTR1_VolSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_U01BTVTR2_VolSv_instMag_i, voltageB);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_U01BTVTR2_VolSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_U01CTVTR3_VolSv_instMag_i, voltageC);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_U01CTVTR3_VolSv_q, q);
            IedServer_updateInt32AttributeValue(iedServer, IEDMODEL_Mod3_MU2_U01NTVTR4_VolSv_instMag_i, voltageN);
            IedServer_updateQuality(iedServer, IEDMODEL_Mod3_MU2_U01NTVTR4_VolSv_q, q);

            IedServer_unlockDataModel(iedServer);
            */

            /* update the values in the SV ASDUs */

            SVPublisher_ASDU_setINT32(asdu1, float1, fVal1);
            SVPublisher_ASDU_setINT32(asdu1, float2, fVal2);
            SVPublisher_ASDU_setINT32(asdu1, float3, fVal3);
            SVPublisher_ASDU_setINT32(asdu1, float7, fVal7);
            SVPublisher_ASDU_setINT32(asdu1, float4, fVal4);
            SVPublisher_ASDU_setINT32(asdu1, float5, fVal5);
            SVPublisher_ASDU_setINT32(asdu1, float6, fVal6);
            SVPublisher_ASDU_setINT32(asdu1, float8, fVal8);

            

            /*
            SVPublisher_ASDU_setINT32(asdu, amp1, currentA);
            SVPublisher_ASDU_setQuality(asdu, amp1q, q);
            SVPublisher_ASDU_setINT32(asdu, amp2, currentB);
            SVPublisher_ASDU_setQuality(asdu, amp2q, q);
            SVPublisher_ASDU_setINT32(asdu, amp3, currentC);
            SVPublisher_ASDU_setQuality(asdu, amp3q, q);
            SVPublisher_ASDU_setINT32(asdu, amp4, currentN);
            SVPublisher_ASDU_setQuality(asdu, amp4q, q);

            SVPublisher_ASDU_setINT32(asdu, vol1, voltageA);
            SVPublisher_ASDU_setQuality(asdu, vol1q, q);
            SVPublisher_ASDU_setINT32(asdu, vol2, voltageB);
            SVPublisher_ASDU_setQuality(asdu, vol2q, q);
            SVPublisher_ASDU_setINT32(asdu, vol3, voltageC);
            SVPublisher_ASDU_setQuality(asdu, vol3q, q);
            SVPublisher_ASDU_setINT32(asdu, vol4, voltageN);
            SVPublisher_ASDU_setQuality(asdu, vol4q, q);
            */

            SVPublisher_ASDU_setTimestamp(asdu1, ts1, ts);

            

            /* update the sample counters */

            SVPublisher_ASDU_increaseSmpCnt(asdu1);

            //fVal1 += 1.1f;
            

            if (svcbEnabled) {

                SVPublisher_ASDU_setINT32(asdu, amp1, currentA);
                SVPublisher_ASDU_setQuality(asdu, amp1q, q);
                SVPublisher_ASDU_setINT32(asdu, amp2, currentB);
                SVPublisher_ASDU_setQuality(asdu, amp2q, q);
                SVPublisher_ASDU_setINT32(asdu, amp3, currentC);
                SVPublisher_ASDU_setQuality(asdu, amp3q, q);
                SVPublisher_ASDU_setINT32(asdu, amp4, currentN);
                SVPublisher_ASDU_setQuality(asdu, amp4q, q);

                SVPublisher_ASDU_setINT32(asdu, vol1, voltageA);
                SVPublisher_ASDU_setQuality(asdu, vol1q, q);
                SVPublisher_ASDU_setINT32(asdu, vol2, voltageB);
                SVPublisher_ASDU_setQuality(asdu, vol2q, q);
                SVPublisher_ASDU_setINT32(asdu, vol3, voltageC);
                SVPublisher_ASDU_setQuality(asdu, vol3q, q);
                SVPublisher_ASDU_setINT32(asdu, vol4, voltageN);
                SVPublisher_ASDU_setQuality(asdu, vol4q, q);

                SVPublisher_ASDU_setRefrTmNs(asdu, Hal_getTimeInNs());

                SVPublisher_ASDU_setSmpCnt(asdu, (uint16_t) sampleCount);

                SVPublisher_publish(svPublisher);
            }
            

            /* send the SV message */
            SVPublisher_publish(svPublisher);
            //printf("%.6f\n", vpico*sin(x));
            /*printf("--------CORRENTES DE LINHA LADO DE ALTA--------\n");
            printf("Corrente da linha A %.6f\n", fVal1);
            printf("Corrente da linha B %.6f\n", fVal2);
            printf("Corrente da linha C %.6f\n", fVal3);
            printf("--------TENSÕES DE LINHA LADO DE BAIXA-------\n");
            printf("Tensão da linha A  %.6f\n", fVal4);
            printf("Tensão da linha B  %.6f\n", fVal5);
            printf("Tensão da linha C  %.6f\n", fVal6);*/
            /*
             * For real applications this sleep time has to be adjusted to match the SV sample rate!
             * Platform specific functions like usleep or timer interrupt service routines have to be used instead
             * to realize the required time accuracy for sending messages.
             */
            Thread_sleep(0.20833);
        }

        SVPublisher_destroy(svPublisher);
    }
    else {
        printf("Failed to create SV publisher\n");
    }
    return 0;
}
