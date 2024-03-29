/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32l0xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define CE_Pin GPIO_PIN_2
#define CE_GPIO_Port GPIOA
#define RED_LASER_Pin GPIO_PIN_3
#define RED_LASER_GPIO_Port GPIOA
#define BUTTON_DOWN_Pin GPIO_PIN_4
#define BUTTON_DOWN_GPIO_Port GPIOA
#define BUTTON_B_Pin GPIO_PIN_5
#define BUTTON_B_GPIO_Port GPIOA
#define BUTTON_A_Pin GPIO_PIN_6
#define BUTTON_A_GPIO_Port GPIOA
#define BUTTON_HOME_Pin GPIO_PIN_7
#define BUTTON_HOME_GPIO_Port GPIOA
#define IR_LASER_Pin GPIO_PIN_0
#define IR_LASER_GPIO_Port GPIOB
#define Y4_Pin GPIO_PIN_9
#define Y4_GPIO_Port GPIOA
#define Y3_Pin GPIO_PIN_10
#define Y3_GPIO_Port GPIOA
#define Y2_Pin GPIO_PIN_11
#define Y2_GPIO_Port GPIOA
#define Y1_Pin GPIO_PIN_12
#define Y1_GPIO_Port GPIOA
#define CSN_Pin GPIO_PIN_15
#define CSN_GPIO_Port GPIOA
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
