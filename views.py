
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse


import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

# Create your views here.
from Remote_User.models import ClientRegister_Model,fake_detection,detection_ratio,detection_accuracy


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def View_Predicted_Tweet_Type_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = ""
    kword = 'Deefake'
    print(kword)
    obj = fake_detection.objects.all().filter(Q(Prediction=kword))
    obj1 = fake_detection.objects.all()
    count = obj.count();
    count1 = obj1.count();
    ratio = (count / count1) * 100
    if ratio != 0:
        detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio1 = ""
    kword1 = 'Real'
    print(kword1)
    obj1 = fake_detection.objects.all().filter(Q(Prediction=kword1))
    obj11 = fake_detection.objects.all()
    count1 = obj1.count();
    count11 = obj11.count();
    ratio1 = (count1 / count11) * 100
    if ratio1 != 0:
        detection_ratio.objects.create(names=kword1, ratio=ratio1)



    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Predicted_Tweet_Type_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Predicted_Tweet_Type(request):
    obj =fake_detection.objects.all()
    return render(request, 'SProvider/View_Predicted_Tweet_Type.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Predicted_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Datasets.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = fake_detection.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:

        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Tid, font_style)
        ws.write(row_num, 1, my_row.published, font_style)
        ws.write(row_num, 2, my_row.title, font_style)
        ws.write(row_num, 3, my_row.tweet, font_style)
        ws.write(row_num, 4, my_row.type, font_style)
        ws.write(row_num, 5, my_row.Prediction, font_style)

    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    df = pd.read_csv('Datasets.csv', encoding='latin-1')

    def apply_response(Label):
        if (Label == "Real"):
            return 0
        elif (Label =="Fake"):
            return 1


    df['results'] = df['Label'].apply(apply_response)


    X = df['tweet']
    y = df['results']

    print("Tweet")
    print(X)
    print("Results")
    print(y)

    cv = CountVectorizer()
    X = cv.fit_transform(X)

    models = []
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)
    X_train.shape, X_test.shape, y_train.shape

    print("Convolutional Neural Network--CNN")
    from sklearn.neural_network import MLPClassifier
    mlpc = MLPClassifier().fit(X_train, y_train)
    y_pred = mlpc.predict(X_test)
    testscore_mlpc = accuracy_score(y_test, y_pred)
    accuracy_score(y_test, y_pred)
    print(accuracy_score(y_test, y_pred))
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('MLPClassifier', mlpc))
    detection_accuracy.objects.create(names="Convolutional Neural Network--CNN",
                                      ratio=accuracy_score(y_test, y_pred) * 100)

    # SVM Model
    print("SVM")
    from sklearn import svm
    lin_clf = svm.LinearSVC()
    lin_clf.fit(X_train, y_train)
    predict_svm = lin_clf.predict(X_test)
    svm_acc = accuracy_score(y_test, predict_svm) * 100
    print(svm_acc)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, predict_svm, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, predict_svm))
    models.append(('svm', lin_clf))
    detection_accuracy.objects.create(names="SVM", ratio=svm_acc)

    print("Logistic Regression")

    from sklearn.linear_model import LogisticRegression
    reg = LogisticRegression(random_state=0, solver='lbfgs', max_iter=1500).fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, y_pred) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, y_pred, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, y_pred))
    models.append(('logistic', reg))
    detection_accuracy.objects.create(names="Logistic Regression", ratio=accuracy_score(y_test, y_pred) * 100)

    print("Decision Tree Classifier")
    from sklearn.tree import DecisionTreeClassifier
    dtc = DecisionTreeClassifier()
    dtc.fit(X_train, y_train)
    dtcpredict = dtc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, dtcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, dtcpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, dtcpredict))
    models.append(('DecisionTreeClassifier', dtc))
    detection_accuracy.objects.create(names="Decision Tree Classifier", ratio=accuracy_score(y_test, dtcpredict) * 100)

    print("KNeighborsClassifier")
    from sklearn.neighbors import KNeighborsClassifier
    kn = KNeighborsClassifier()
    kn.fit(X_train, y_train)
    knpredict = kn.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, knpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, knpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, knpredict))
    models.append(('KNeighborsClassifier', kn))
    detection_accuracy.objects.create(names="KNeighborsClassifier", ratio=accuracy_score(y_test, knpredict) * 100)

    print("Random Forest Classifier")
    from sklearn.ensemble import RandomForestClassifier
    rf_clf = RandomForestClassifier()
    rf_clf.fit(X_train, y_train)
    rfpredict = rf_clf.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, rfpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, rfpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, rfpredict))
    models.append(('RandomForestClassifier', rf_clf))
    detection_accuracy.objects.create(names="Random Forest Classifier", ratio=accuracy_score(y_test, rfpredict) * 100)

    print("AdaBoost Classifier")
    from sklearn.ensemble import AdaBoostClassifier
    ac = AdaBoostClassifier()
    ac.fit(X_train, y_train)
    acpredict = ac.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, acpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, acpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, acpredict))
    models.append(('AdaBoostClassifier', ac))
    detection_accuracy.objects.create(names="AdaBoost Classifier", ratio=accuracy_score(y_test, acpredict) * 100)

    print("Stochastic Gradient Descent Classifier")
    from sklearn.linear_model import SGDClassifier
    sgc = SGDClassifier()
    sgc.fit(X_train, y_train)
    sgcpredict = sgc.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, sgcpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, sgcpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, sgcpredict))
    models.append(('SGDClassifier', sgc))
    detection_accuracy.objects.create(names="Stochastic Gradient Descent Classifier", ratio=accuracy_score(y_test, sgcpredict) * 100)

    print("Gradient Boosting Machine")
    from sklearn.ensemble import GradientBoostingClassifier
    gbm = GradientBoostingClassifier()
    gbm.fit(X_train, y_train)
    gbmpredict = gbm.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, gbmpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, gbmpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, gbmpredict))
    models.append(('GradientBoostingClassifier', gbm))
    detection_accuracy.objects.create(names="Gradient Boosting Machine", ratio=accuracy_score(y_test, gbmpredict) * 100)

    print("Naive Bayes")
    from sklearn.naive_bayes import MultinomialNB
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    nbpredict = nb.predict(X_test)
    print("ACCURACY")
    print(accuracy_score(y_test, nbpredict) * 100)
    print("CLASSIFICATION REPORT")
    print(classification_report(y_test, nbpredict, zero_division=1))
    print("CONFUSION MATRIX")
    print(confusion_matrix(y_test, nbpredict))
    models.append(('Naive Bayes', nb))
    detection_accuracy.objects.create(names="Naive Bayes", ratio=accuracy_score(y_test, nbpredict) * 100)


    csv_format = 'Results.csv'
    df.to_csv(csv_format, index=False)
    df.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})