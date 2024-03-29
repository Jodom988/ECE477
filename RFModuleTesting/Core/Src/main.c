/* USER CODE BEGIN Header */
/**
******************************************************************************
* @file           : main.c
* @brief          : Main program body
******************************************************************************
* @attention
*
* <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
* All rights reserved.</center></h2>
*
* This software component is licensed by ST under BSD 3-Clause license,
* the "License"; You may not use this file except in compliance with the
* License. You may obtain a copy of the License at:
*                        opensource.org/licenses/BSD-3-Clause
*
******************************************************************************
*/
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "MY_NRF24.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define USB_ADDR 0x11223344AA
#define PI_ADDR 0x5566778899

#define RX_ADDR 0x4444444444
#define CHANNEL 120
#define RX_PIPE 1
#define PAYLOAD_SIZE 5

#define RF_CLICK_LEFT 0x01
#define RF_CLICK_RIGHT 0x02
#define RF_CLICK_LEFT_RELEASE 0x03
#define RF_CLICK_RIGHT_RELEASE 0x04

#define RF_CALIBRATE_START 0x10
#define RF_CALIBRATE_CORNER 0x11
#define RF_COMMAND_LASER_ON 0x12
#define RF_CALIBRATE_CORNER_RESULT 0x13
#define RF_CALIBRATE_EXIT 0x14
#define RF_CALIBRATE_RESULT 0X15
#define RF_CALIBRATE_FAIL 0x00
#define RF_GET_BASE 0x30

#define RF_LASERS_ON 0x20
#define RF_LASERS_OFF 0x21
#define RF_IR_ON 0x22
#define RF_IR_OFF 0x23
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc;

SPI_HandleTypeDef hspi1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
static void MX_ADC_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
void read_regs()
{
  uint8_t config = NRF24_read_register(REG_CONFIG);
  uint8_t en_aa = NRF24_read_register(REG_EN_AA);
  uint8_t en_rxaddr = NRF24_read_register(REG_EN_RXADDR);
  uint8_t setup_aw = NRF24_read_register(REG_SETUP_AW);
  uint8_t setup_retr = NRF24_read_register(REG_SETUP_RETR);
  uint8_t ch = NRF24_read_register(REG_RF_CH);
  uint8_t rf_setup = NRF24_read_register(REG_RF_SETUP);

  uint8_t dynpd = NRF24_read_register(REG_DYNPD);
  uint8_t feature = NRF24_read_register(REG_FEATURE);

  uint8_t pipe0_addr[5];
  NRF24_read_registerN(0x0A, pipe0_addr, 5);

  uint8_t pipe1_addr[5];
  NRF24_read_registerN(0x0A+1, pipe0_addr, 5);
  uint8_t a = pipe0_addr[4];
  return;
}

void reset_packages_lost()
{
	NRF24_ce(0);
	NRF24_setChannel(CHANNEL-1);
	HAL_Delay(100);
	NRF24_setChannel(CHANNEL);
	HAL_Delay(100);
	NRF24_ce(1);
}

void send_RF_packet(uint8_t command, uint64_t addr)
{
  uint8_t tx_data[5] = "Hello";
  tx_data[0] = command;
  NRF24_stopListening();

  NRF24_openWritingPipe(addr);

  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);

  return;
}

void send_RF_corner(uint8_t corner_num)
{
  uint8_t tx_data[5] = "Hello";
  tx_data[0] = RF_CALIBRATE_CORNER;
  tx_data[1] = corner_num;
  NRF24_stopListening();

  NRF24_openWritingPipe(PI_ADDR);

  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);
  NRF24_write(tx_data,5);
  HAL_Delay(50);




  return;
}

void corner(uint16_t led_number, int payloadSize, int corner_num) {
	// Turn on LED while processing this corner
	HAL_GPIO_WritePin(GPIOA, led_number, GPIO_PIN_SET);

	// wait for DOWN press, then debounce
	while(HAL_GPIO_ReadPin(BUTTON_DOWN_GPIO_Port, BUTTON_DOWN_Pin) == 0);
	HAL_Delay(100);
	// turn laser on, sending GET_BASE, delaying, and LASER_ON
	send_RF_packet(RF_GET_BASE, PI_ADDR); // Send that the lasers are about to toggle
	HAL_Delay(500); // delay, instead of ACK
	send_RF_packet(RF_LASERS_ON, PI_ADDR);

	HAL_GPIO_WritePin(RED_LASER_GPIO_Port, RED_LASER_Pin, GPIO_PIN_SET); // Turn red laser ON
	HAL_GPIO_WritePin(IR_LASER_GPIO_Port, IR_LASER_Pin, GPIO_PIN_SET); // Turn IR laser ON

	// wait for B to send CORNER
	while(HAL_GPIO_ReadPin(BUTTON_HOME_GPIO_Port, BUTTON_HOME_Pin) == 0);
	// THen send calibration signals
	send_RF_corner(corner_num);

	HAL_Delay(500); // delay, instead of ACK

	// turn laser off
	send_RF_packet(RF_LASERS_OFF, PI_ADDR);


  HAL_GPIO_WritePin(RED_LASER_GPIO_Port, RED_LASER_Pin, GPIO_PIN_RESET); // Turn red laser ON
  HAL_GPIO_WritePin(IR_LASER_GPIO_Port, IR_LASER_Pin, GPIO_PIN_RESET); // Turn IR laser ON


  HAL_GPIO_WritePin(GPIOA, led_number, GPIO_PIN_RESET);
  HAL_Delay(100);
}


/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_SPI1_Init();
  MX_ADC_Init();
  /* USER CODE BEGIN 2 */
  NRF24_begin(CSN_GPIO_Port, CSN_Pin, CE_Pin, hspi1);

  int LASER_ON = 0;


  NRF24_stopListening();
  NRF24_openWritingPipe(PI_ADDR);
  NRF24_setAutoAck(true);
  NRF24_setChannel(CHANNEL);
  NRF24_setPayloadSize(PAYLOAD_SIZE);
  NRF24_setDataRate(RF24_250KBPS);
  //NRF24_write(myTxData, 5);
  //send_RF_packet(RF_GET_BASE, PI_ADDR);
  //send_RF_packet(RF_CLICK_LEFT, USB_ADDR);
  HAL_Delay(250);
  //send_RF_packet(RF_CLICK_LEFT_RELEASE, USB_ADDR);
  //read_regs();


  uint16_t raw;


  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    //	  if (NRF24_available()) {
    //		  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_10);
    //		  NRF24_read(rxdata, PAYLOAD_SIZE);
    //		  uint8_t msg =rxdata[0];
    //		  HAL_Delay(250);
    //	  }
    //	  else {
    //		  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_9);
    //		  read_regs();
    //		  HAL_Delay(250);
    //
    //	  }

    //		if(NRF24_write(myTxData, 5))
    //		{
    //			  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_10);
    //			  HAL_Delay(500);
    //		}
    //
    //		  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_9);
    //		HAL_Delay(250);

    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_4))
    {
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_SET);	//Turn on yellow pin
      HAL_Delay(100); // debounce


      if (LASER_ON) {
		send_RF_packet(RF_LASERS_OFF, PI_ADDR); // Send that the lasers are about to toggle
		LASER_ON = 0;
		HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET); // Turn red laser ON
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET); // Turn IR laser ON
      }
      else {
		send_RF_packet(RF_GET_BASE, PI_ADDR); // Send that the lasers are about to turn on
		LASER_ON = 1;
		HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET); // Turn red laser ON
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET); // Turn IR laser ON
		send_RF_packet(RF_LASERS_ON, PI_ADDR); // Send that the lasers are on

      }
      HAL_Delay(1000);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_RESET); // Turn off yellow 4


      HAL_Delay(1000);

    }

    // A is PA6
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_6))
    {
      send_RF_packet(RF_CLICK_LEFT, USB_ADDR); // Send left click
      //send_RF_packet(RF_GET_BASE, PI_ADDR); // Send left click
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_SET); // Turn off yellow 4
      HAL_Delay(500);
      while (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_6)) {
        HAL_Delay(100);
      }
      send_RF_packet(RF_CLICK_LEFT_RELEASE, USB_ADDR);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_12, GPIO_PIN_RESET); // Turn off yellow 4
      HAL_Delay(100);
    }

    // B is PA5
    if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_5))
    {
      send_RF_packet(RF_CLICK_RIGHT, USB_ADDR); // Send right click
      HAL_Delay(100);
      while (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_5)) {
        HAL_Delay(100);
      }
      send_RF_packet(RF_CLICK_RIGHT_RELEASE, USB_ADDR);
      HAL_Delay(100);
    }

    // 2 is PC14
    if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_14))
    {
      // ADC stuff
      HAL_ADC_Start(&hadc);
      HAL_ADC_PollForConversion(&hadc, HAL_MAX_DELAY);
      raw = HAL_ADC_GetValue(&hadc);

      if (raw >= 2950) // red at 2950, green anywhere below that. 2.2 V
      {
        HAL_GPIO_WritePin(GPIOC, GPIO_PIN_15, GPIO_PIN_SET); // Turn on the green LEDs
      }
      else
      {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, GPIO_PIN_SET); // Turn on the red LEDs
      }

      HAL_Delay(3000);
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_15, GPIO_PIN_RESET); // Turn off the red LEDs
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, GPIO_PIN_RESET); // Turn off the red LEDs
    }

    // 1 is PB7
    if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_7))
    {

		if (LASER_ON) {
			send_RF_packet(RF_LASERS_OFF, PI_ADDR); // Send that the lasers are about to toggle
			HAL_Delay(250);
			LASER_ON = 0;
			HAL_GPIO_WritePin(RED_LASER_GPIO_Port, RED_LASER_Pin, GPIO_PIN_RESET); // Turn red laser OFF
			HAL_GPIO_WritePin(IR_LASER_GPIO_Port , IR_LASER_Pin , GPIO_PIN_RESET); // Turn IR  laser OFF
		}

      send_RF_packet(RF_CALIBRATE_START, PI_ADDR); // Send calibration mode

      // Press B on the top left corner of the screen
      corner(GPIO_PIN_12, PAYLOAD_SIZE, 1);
      corner(GPIO_PIN_11, PAYLOAD_SIZE, 2);
      corner(GPIO_PIN_10, PAYLOAD_SIZE, 3);
      corner(GPIO_PIN_9,  PAYLOAD_SIZE, 4);

      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_15, GPIO_PIN_SET); // Turn on the green LEDs
      HAL_Delay(3000);
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_15, GPIO_PIN_RESET); // Turn off the red LEDs

      send_RF_packet(RF_CALIBRATE_EXIT, PI_ADDR); // Send calibration mode

    }

  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSICalibrationValue = 0;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_5;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC_Init(void)
{

  /* USER CODE BEGIN ADC_Init 0 */

  /* USER CODE END ADC_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC_Init 1 */

  /* USER CODE END ADC_Init 1 */
  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc.Instance = ADC1;
  hadc.Init.OversamplingMode = DISABLE;
  hadc.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV1;
  hadc.Init.Resolution = ADC_RESOLUTION_12B;
  hadc.Init.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;
  hadc.Init.ScanConvMode = ADC_SCAN_DIRECTION_FORWARD;
  hadc.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc.Init.ContinuousConvMode = DISABLE;
  hadc.Init.DiscontinuousConvMode = DISABLE;
  hadc.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc.Init.DMAContinuousRequests = DISABLE;
  hadc.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc.Init.LowPowerAutoWait = DISABLE;
  hadc.Init.LowPowerFrequencyMode = ENABLE;
  hadc.Init.LowPowerAutoPowerOff = DISABLE;
  if (HAL_ADC_Init(&hadc) != HAL_OK)
  {
    Error_Handler();
  }
  /** Configure for the selected ADC regular channel to be converted.
  */
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = ADC_RANK_CHANNEL_NUMBER;
  if (HAL_ADC_ConfigChannel(&hadc, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC_Init 2 */

  /* USER CODE END ADC_Init 2 */

}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_256;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 7;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_15, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1|CE_Pin|RED_LASER_Pin|Y4_Pin
                          |Y3_Pin|Y2_Pin|Y1_Pin|CSN_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(IR_LASER_GPIO_Port, IR_LASER_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC14 */
  GPIO_InitStruct.Pin = GPIO_PIN_14;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : PC15 */
  GPIO_InitStruct.Pin = GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : PA1 CE_Pin RED_LASER_Pin Y4_Pin
                           Y3_Pin Y2_Pin Y1_Pin CSN_Pin */
  GPIO_InitStruct.Pin = GPIO_PIN_1|CE_Pin|RED_LASER_Pin|Y4_Pin
                          |Y3_Pin|Y2_Pin|Y1_Pin|CSN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : BUTTON_DOWN_Pin BUTTON_B_Pin BUTTON_A_Pin BUTTON_HOME_Pin */
  GPIO_InitStruct.Pin = BUTTON_DOWN_Pin|BUTTON_B_Pin|BUTTON_A_Pin|BUTTON_HOME_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : IR_LASER_Pin */
  GPIO_InitStruct.Pin = IR_LASER_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(IR_LASER_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : PB1 PB6 PB7 */
  GPIO_InitStruct.Pin = GPIO_PIN_1|GPIO_PIN_6|GPIO_PIN_7;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1)
    {
    }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
    /* User can add his own implementation to report the file name and line number,
    ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
