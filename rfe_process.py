import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss

from features.data_provider import all_features, DataLoader
from models.helpers import get_feature_importance

feature_set = all_features.copy()

params = {
    'oob_score' : True,
    'bootstrap': True,
    'n_jobs':-1,
    'n_estimators': 1000,
    "max_features": "sqrt",
    "max_depth": 8,
    "min_samples_leaf": 3
}

avg_accuracies = []
avg_log_lossss = []
features = []

while len(feature_set) > 0:
    data_loader = DataLoader(feature_set)

    accuracies = []
    log_losses = []
    feature_values = {}
    for i in range(100):
        model = RandomForestClassifier(**params)

        X_train, y_train, X_test, y_test = data_loader.get_train_and_test_dataset("home_win", random_state=None)
        model.fit(X_train, y_train)

        y_true, y_pred = y_test, model.predict(X_test)
        accuracies.append(accuracy_score(y_true, y_pred))
        y_true, y_prob = y_test, model.predict_proba(X_test)
        log_losses.append(log_loss(y_true, y_prob))

        feature_dict = get_feature_importance(model.feature_importances_, feature_set)
        for key, value in feature_dict.items():
            if key in feature_values:
                feature_values[key] = feature_values[key] + [value]
            else:
                feature_values[key] = [value]

    feature_scores = []
    for key, value in feature_values.items():
        feature_scores.append((key, np.mean(value)))

    feature_scores = sorted(feature_scores, key = lambda t: t[1], reverse=True)
    last_feature, _ = feature_scores[-1]

    feature_set.remove(last_feature)

    features.append(feature_set.copy())
    avg_accuracies.append(np.mean(accuracies))
    avg_log_lossss.append(np.mean(log_losses))

data = {
    "features": features,
    "accuracy": avg_accuracies,
    "log_loss": avg_log_lossss
}

with open('rfe_outcome_model.pickle', 'wb') as handle:
    pickle.dump(data, handle)
