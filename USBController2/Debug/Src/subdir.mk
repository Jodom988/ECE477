################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Src/MY_NRF24.c \
../Src/main.c \
../Src/stm32f7xx_hal_msp.c \
../Src/stm32f7xx_it.c \
../Src/syscalls.c \
../Src/system_stm32f7xx.c 

OBJS += \
./Src/MY_NRF24.o \
./Src/main.o \
./Src/stm32f7xx_hal_msp.o \
./Src/stm32f7xx_it.o \
./Src/syscalls.o \
./Src/system_stm32f7xx.o 

C_DEPS += \
./Src/MY_NRF24.d \
./Src/main.d \
./Src/stm32f7xx_hal_msp.d \
./Src/stm32f7xx_it.d \
./Src/syscalls.d \
./Src/system_stm32f7xx.d 


# Each subdirectory must supply rules for building sources it contributes
Src/%.o: ../Src/%.c
	@echo 'Building file: $<'
	@echo 'Invoking: MCU GCC Compiler'
	@echo $(PWD)
	arm-none-eabi-gcc -mcpu=cortex-m7 -mthumb -mfloat-abi=soft -DUSE_HAL_DRIVER -DSTM32F746xx -I"/Users/joseluistejada/Desktop/USBController2/Inc" -I"/Users/joseluistejada/Desktop/USBController2/Drivers/STM32F7xx_HAL_Driver/Inc" -I"/Users/joseluistejada/Desktop/USBController2/Drivers/STM32F7xx_HAL_Driver/Inc/Legacy" -I"/Users/joseluistejada/Desktop/USBController2/Drivers/CMSIS/Device/ST/STM32F7xx/Include" -I"/Users/joseluistejada/Desktop/USBController2/Drivers/CMSIS/Include"  -Og -g3 -Wall -fmessage-length=0 -ffunction-sections -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


