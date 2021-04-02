################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Src/MY_NRF24.c \
../Src/main.c \
../Src/stm32f4xx_hal_msp.c \
../Src/stm32f4xx_it.c \
../Src/syscalls.c \
../Src/system_stm32f4xx.c \
../Src/usb_device.c \
../Src/usbd_conf.c \
../Src/usbd_desc.c 

OBJS += \
./Src/MY_NRF24.o \
./Src/main.o \
./Src/stm32f4xx_hal_msp.o \
./Src/stm32f4xx_it.o \
./Src/syscalls.o \
./Src/system_stm32f4xx.o \
./Src/usb_device.o \
./Src/usbd_conf.o \
./Src/usbd_desc.o 

C_DEPS += \
./Src/MY_NRF24.d \
./Src/main.d \
./Src/stm32f4xx_hal_msp.d \
./Src/stm32f4xx_it.d \
./Src/syscalls.d \
./Src/system_stm32f4xx.d \
./Src/usb_device.d \
./Src/usbd_conf.d \
./Src/usbd_desc.d 


# Each subdirectory must supply rules for building sources it contributes
Src/%.o: ../Src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU GCC Compiler'
	@echo $(PWD)
	arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -DUSE_HAL_DRIVER -DSTM32F446xx -I"/Users/joseluistejada/Desktop/USBController/Inc" -I"/Users/joseluistejada/Desktop/USBController/Drivers/STM32F4xx_HAL_Driver/Inc" -I"/Users/joseluistejada/Desktop/USBController/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy" -I"/Users/joseluistejada/Desktop/USBController/Middlewares/ST/STM32_USB_Device_Library/Core/Inc" -I"/Users/joseluistejada/Desktop/USBController/Middlewares/ST/STM32_USB_Device_Library/Class/HID/Inc" -I"/Users/joseluistejada/Desktop/USBController/Drivers/CMSIS/Device/ST/STM32F4xx/Include" -I"/Users/joseluistejada/Desktop/USBController/Drivers/CMSIS/Include"  -Og -g3 -Wall -fmessage-length=0 -ffunction-sections -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


