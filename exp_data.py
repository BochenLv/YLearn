import numpy as np
import pandas as pd


def meaningless_discrete_dataset_(num, treatment_effct,
                                  confounder_n=2,
                                  w_var=5,
                                  eps=1e-4,
                                  data_frame=True,
                                  random_seed=2022,
                                  instrument=False):
    """Generate a dataset where the treatment and outcome have some
    confounders while the relation between the treatment and outcome
    is linear. The treatment is an array of integers where each integer
    indicates the treatment group assigned to the corresponding example.
    The outcome is an array of float, i.e., we are building continuous
    outcome.

    Parameters
    ----------
    num : int
        The number of examples in the dataset.
    confounder_n : int
        The number of confounders of the treatment and outcome.
    treatment_effct : list, optional. Defaults to None.
    w_var : float, optional. Defaults to 0.5.
        Variance of the confounder around its mean.
    eps : float, optional. Defaults to 1e-4.
        Noise level imposed to the data generating process.
    data_frame : bool, optional. Defaults to True.
        Return pandas.DataFrame if True.
    random_seed : int, optional. Defaults to 2022.
    instrument : bool, optional. Defaults to False.
        Add instrument variables to the dataset if True.

    Returns
    ----------
    pandas.DataFrame, optional.
        w_j's are confounders of outcome and treatment.
    """
    np.random.seed(random_seed)

    # Build treatment x which depends on the confounder w
    x_num = len(treatment_effct)
    w = [
        np.random.normal(0, w_var*np.random.random_sample(), size=(num, 1))
        for i in range(confounder_n)
    ]
    w = np.concatenate(tuple(w), axis=1)
    w_coef = np.random.rand(x_num, confounder_n)
    x = w.dot(w_coef.T) + np.random.normal(0, eps, size=(num, x_num))
    if instrument:
        z = None
    x = x.argmax(axis=1)
    x_one_hot = np.eye(x_num)[x]

    # Now we build the outcome y which depends on both x and w
    x_coef = np.random.randn(1, confounder_n)
    x_coef = np.concatenate(
        (np.array(treatment_effct).reshape(1, -1), x_coef), axis=1
    )
    x_ = np.concatenate((x_one_hot, w), axis=1)
    y = x_.dot(x_coef.T) + np.random.normal(0, eps, size=(num, 1))

    # Return the dataset
    if data_frame:
        data_dict = {}
        data_dict['treatment'] = x
        if instrument:
            data_dict['instrument'] = z
        for i, j in enumerate(w.T):
            data_dict[f'w_{i}'] = j
        data_dict['outcome'] = y.reshape(num,)
        data = pd.DataFrame(data_dict)
        return data
    else:
        if instrument:
            return (x, w, z, y)
        else:
            return (x, w, y)


def coupon_dataset(n_users, treatment_style='binary', with_income=False):
    if with_income:
        income = np.random.normal(500, scale=15, size=n_users)
        gender = np.random.randint(0, 2, size=n_users)
        coupon = gender * 20 + 110 + income / 50 \
            + np.random.normal(scale=5, size=n_users)
        if treatment_style == 'binary':
            coupon = (coupon > 120).astype(int)
        amount = coupon * 150 + gender * 100 + 150 \
            + income / 5 + np.random.normal(size=n_users)
        time_spent = coupon * 10 + amount / 10

        df = pd.DataFrame({
            'gender': gender,
            'coupon': coupon,
            'amount': amount,
            'income': income,
            'time_spent': time_spent,
        })
    else:
        gender = np.random.randint(0, 2, size=n_users)
        coupon = gender * 20 + 150 + np.random.normal(scale=5, size=n_users)
        if treatment_style == 'binary':
            coupon = (coupon > 150).astype(int)
        amount = coupon * 30 + gender * 100 \
            + 150 + np.random.normal(size=n_users)
        time_spent = coupon * 100 + amount / 10

        df = pd.DataFrame({
            'gender': gender,
            'coupon': coupon,
            'amount': amount,
            'time_spent': time_spent,
        })

    return df


def meaningless_discrete_dataset(num, confounder_n,
                                 treatment_effct=None,
                                 prob=None,
                                 w_var=0.5,
                                 eps=1e-4,
                                 coef_range=5e4,
                                 data_frame=True,
                                 random_seed=2022):
    np.random.seed(random_seed)
    samples = np.random.multinomial(num, prob)
    # build treatment x with shape (num,), where the number of types
    # of treatments is len(prob) and each treatment i is assigned a
    # probability prob[i]
    x = []
    for i, sample in enumerate(samples):
        x += [i for j in range(sample)]
    np.random.shuffle(x)

    # construct the confounder w
    w = [
        np.random.normal(0, w_var, size=(num,)) for i in range(confounder_n)
    ]
    for i, w_ in enumerate(w, 1):
        x = x + w_
    x = np.round(x).astype(int)
    for i, j in enumerate(x):
        if j > len(prob) - 1:
            x[i] = len(prob) - 1
        elif j < 0:
            x[i] = 0

    # construct the outcome y
    coef = np.random.randint(int(coef_range*eps), size=(confounder_n,))
    y = np.random.normal(eps, size=(num,))
    for i in range(len(y)):
        y[i] = y[i] + treatment_effct[x[i]] * x[i]
    for i, j in zip(coef, w):
        y += i * j

    if data_frame:
        data_dict = {}
        data_dict['treatment'] = x
        for i, j in enumerate(w):
            data_dict[f'w_{i}'] = j
        data_dict['outcome'] = y
        data = pd.DataFrame(data_dict)
        return data, coef
    else:
        return (x, w, y, coef)
