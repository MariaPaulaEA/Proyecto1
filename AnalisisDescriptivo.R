#Proyecto 1

setwd("/Users/paulaescobar/Documents/ACTD/Proyecto1")

library(FrF2)
library(LSD)
library(plyr)
library(psych)
library(ggplot2)
library(MASS)
library(plotrix)
library(Publish)
library(datasets)
library(car)
library(agricolae)
library(aod)

#Attributes: 8 symbolic, 6 numeric.
#  Age; sex; chest pain type (angina, abnang, notang, asympt);
#  Trestbps (resting blood pres); cholesteral; fasting blood sugar < 120
#  (true or false); resting ecg (norm, abn, hyper); max heart rate achieved;
#  exercise induced angina (true or false); oldpeak; slope (up, flat, down)
#  number of major vessels (0-3) colored by flourosopy; thal (norm, fixed, rever).
#  Finally, the class (diagnosis of heart disease) is either healthy (buff) or
#  with heart-disease (sick).

data <- read.csv(file = "processed.cleveland.data.csv", header = FALSE)
colnames(data) <- c('Age', 'Sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach',
                    'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num')
data$ca <- as.numeric(data$ca)
data$thal <- as.numeric(data$thal)
summary(data)
data <- na.omit(data)

#Rangos de colesterol para ANOVA

data$colesterol <- c()

for (i in 1:length(data$chol)) {
  if (data$chol[i] < 200) {
    data$colesterol[i] <- 0
  }
  
  else if (data$chol[i] >= 240) {
    data$colesterol[i] <- 2
  }
  
  else if (data$chol[i] < 240 && data$chol[i] >= 200) {
    data$colesterol[i] <- 1
  }
}

#Descriptivo para continuas

a <- describe(data$Age)
b <- describe(data$trestbps)
c <- describe(data$chol)
d <- describe(data$thalach)
e <- describe(data$oldpeak)

des <- data.frame(a)
des[2,] <- b
des[3,] <- c
des[4,] <- d
des[5,] <- e

rownames(des) <- c("Age", 'Trestbps', 'Chol', 'Thalch', 'Oldpeak')
des[,2:13]

#Barras para discretas

par(mfrow=c(3,3))
par(mfrow=c(1,1))

tabla <- table(data$num)
barplot(tabla, main = "Frecuencia de Diagnóstico", xlab = "Diagnóstico", ylab = "Frecuencia", col = 1)

tabla <- table(data$Sex)
barplot(tabla, main = "Frecuencia de Sexo", xlab = "Sexo", ylab = "Frecuencia", col = 7)

tabla <- table(data$cp)
barplot(tabla, main = "Frecuencia de Tipo de dolor en el pecho", xlab = "Tipo de dolor en el pecho", ylab = "Frecuencia", col = 2)

tabla <- table(data$fbs)
barplot(tabla, main = "Frecuencia de Azúcar en la sangre en ayunas (< 120)", xlab = "Azúcar en la sangre en ayunas (< 120)", ylab = "Frecuencia", col = 3)

tabla <- table(data$restecg)
barplot(tabla, main = "Frecuencia de Resultados de electrocardiograma en reposo", xlab = "Resultados de electrocardiograma en reposo", ylab = "Frecuencia", col = 4)

tabla <- table(data$exang)
barplot(tabla, main = "Frecuencia de Angina inducida por el ejercicio", xlab = "Angina inducida por el ejercicio", ylab = "Frecuencia", col = 5)

tabla <- table(data$slope)
barplot(tabla, main = "Frecuencia de Pendiente del segmento ST", xlab = "Pendiente del segmento ST", ylab = "Frecuencia", col = 6)

tabla <- table(data$ca)
barplot(tabla, main = "Frecuencia de Número de vasos coloreados por fluoroscopia", xlab = "Número de vasos coloreados por fluoroscopia", ylab = "Frecuencia", col = 8)

tabla <- table(data$thal)
barplot(tabla, main = "Frecuencia de Estado del corazón según Thallium", xlab = "Estado del corazón según Thallium", ylab = "Frecuencia")

#Histogramas para continuas

par(mfrow=c(3,2))
par(mfrow=c(1,1))
hist(data$Age, xlab = "Edad", main = "Histograma de Edad", col = 2)
hist(data$trestbps, xlab = "Resting Blood Pressure", main = "Histograma de Resting Blood Pressure", col = 3)
hist(data$chol, xlab = "Colesterol", main = "Histograma de Colesterol", col = 4)
hist(data$thalach, xlab = "Max heart rate achieved", main = "Histograma de Max heart rate achieved", col = 5)
hist(data$oldpeak, xlab = "Oldpeak", main = "Histograma de Oldpeak", col = 6)

#Num en relación con variables discretas

tabla <- data.frame(table(data$Sex, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "orange") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Sexo") + ylab("Diagnóstico")

tabla <- data.frame(table(data$cp, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "red") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Dolor en el pecho") + ylab("Diagnóstico")

tabla <- data.frame(table(data$fbs, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "green") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Azúcar en la sangre en ayunas") + ylab("Diagnóstico")

tabla <- data.frame(table(data$restecg, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "dark blue") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Resultados de electrocardiograma en reposo") + ylab("Diagnóstico")

tabla <- data.frame(table(data$exang, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "blue") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Angina inducida por el ejercicio") + ylab("Diagnóstico")

tabla <- data.frame(table(data$slope, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "purple") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Pendiente del segmento ST") + ylab("Diagnóstico")

tabla <- data.frame(table(data$ca, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "dark green") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Número de vasos principales coloreados por fluoroscopia") + ylab("Diagnóstico")

tabla <- data.frame(table(data$thal, data$num))
ggplot(tabla, aes(x = Var1, y = Var2, size = Freq)) + geom_point(alpha = 0.7, color = "black") + scale_size(range = c(.1, 14), name = "Frecuencia") + xlab("Estado del corazón según prueba Thallium") + ylab("Diagnóstico")


#Num en relación con variables continuas

plot(x = data$num, y = data$chol, xlab = "Diagnóstico", ylab = "Colesterol", main = "Colesterol en función del Diagnóstico")


#Diagramas de caja para continuas

boxplot(data$Age, ylab = "Edad", col = 2)
boxplot(data$trestbps, ylab = "Resting Blood Pressure", col = 3)
boxplot(data$chol, ylab = "Colesterol", col = 4)
boxplot(data$thalach, ylab = "Max heart rate achieved", col = 5)
boxplot(data$oldpeak, ylab = "Oldpeak", col = 6)

summary(data$Age)
summary(data$trestbps)
summary(data$chol)
summary(data$thalach)
summary(data$oldpeak)

#Diagramas de dispersión

continuas <- data.frame(data$Age, data$trestbps, data$chol, data$thalach, data$oldpeak)
colnames(continuas) <- c("Age", 'trestbps', 'chol', 'thalach', 'oldpeak')
pairs(continuas)

#Correlaciones continuas

pairs(continuas)
M <- cor(continuas)

#ANOVA completo

data$Age <- as.factor(data$Age)
data$Sex <- as.factor(data$Sex)
data$cp <- as.factor(data$cp)
data$trestbps <- as.factor(data$trestbps)
data$chol <- as.factor(data$chol)
data$fbs <- as.factor(data$fbs)
data$restecg <- as.factor(data$restecg)
data$thalach <- as.factor(data$thalach)
data$exang <- as.factor(data$exang)
data$oldpeak <- as.factor(data$oldpeak)
data$slope <- as.factor(data$slope)
data$ca <- as.factor(data$ca)
data$thal <- as.factor(data$thal)
data$colesterol <- as.factor(data$colesterol)

anova1 <- aov(num ~ Sex+Age+cp+trestbps+colesterol+fbs+restecg+thalach+exang+oldpeak+slope+ca+thal, data = data)
summary(anova1)

#Model adequacy checking
par(mfrow=c(2,2));plot(anova1);par(mfrow=c(1,1))

#Normality assumption
hist(anova1$residuals, xlab = "Residuales", main = "Histograma de residuales modelo completo")
shapiro.test(anova1$residuals)

#Constant variance assumption
lmtest::bptest(anova1)

#No autocorrelation assumption
car::durbinWatsonTest(anova1)